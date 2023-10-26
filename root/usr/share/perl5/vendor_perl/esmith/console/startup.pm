package esmith::console::startup;
use Locale::gettext;
use esmith::console;
use esmith::ConfigDB;
use strict;
use warnings;

sub new
{
    my $class = shift;
    my $self = {
                @_,
               };
    bless $self, $class;
    return $self;
}

sub startup_callback {
    my $fd = shift;
    my @out = ();
    my $done = 0;

    use DirHandle;
    my $d = DirHandle->new("/etc/rc7.d");
    my @services = sort
        {
            $a =~ /^S(\d+)/; my $A = $1;
            $b =~ /^S(\d+)/; my $B = $1;
            $A <=> $B
        } grep { /^S/ } $d->read;
    my $rows = 12;
    my $status_col = 65;

    my $db = esmith::ConfigDB->open_ro;
    my $rec = $db->get('smb');
    my $i=0;
    foreach (@services) {
        $i=$i+1;
        next unless /^S(\d+)([^\.][\.\w\-]+)$/;
        next unless $2 eq "smb";
        splice @services,$i-1 , 1, "S${1}4smbd", "S${1}5nmbd"  unless ($rec and $rec->prop('status') eq 'disabled');
        last;
    }


    open(STDOUT, ">&STDERR");
    foreach (@services)
    {
       sleep 1;
       my $percent = int(($done * 100) / ($#services + 1));
       $done += 1;
       my $link = $_;
       #warn "Looking at symlink $_\n";
       next unless /^S\d+([^\.][\.\w\-]+)$/; # Untaint service name
       my $service = $1;
       #my $db = esmith::ConfigDB->open_ro;
       $rec = $db->get($service);
       do
       {
            warn "not starting disabled service $service\n";
            next;
       } unless ($rec and $rec->prop('status') eq 'enabled');
       my $prompt = "starting ";
       my $supervised = -x "/service/$service/run";
       my @cmd;
       if (-x "/service/$service/run")
       {
            $prompt .= " supervised service $service";
            warn "starting supervised service $service\n";
            @cmd = ("sv", "up", "/service/$service");
       }
       elsif (-x "/etc/init.d/$service")
       {
            $prompt .= " unsupervised service $service";
            warn "starting unsupervised service $service\n";
            @cmd = ("/etc/init.d/$service", "start");
       }
       else
       {
            warn "ignoring unknown service $service: bogus start symlink $link\n";
            next;
       }

       push @out, "$prompt\n";
       print $fd "XXX\n";
       print $fd "$percent\n";
       my @show = $#out > $rows ? @out[$#out - $rows .. $#out] : @out;
       do { print $fd $_ } foreach @show;
       print $fd "XXX\n";
       $prompt .= " " x ($status_col - length($prompt));
       $prompt .= system(@cmd) ? "\\Z1FAILED\\Zn" : "\\Z2OK\\Zn";
       $out[-1] = "$prompt\n";
       @show = $#out > $rows ? @out[$#out - $rows .. $#out] : @out;
       print $fd "XXX\n";
       print $fd "$percent\n";
       do { print $fd $_ } foreach @show;
       print $fd "XXX\n";
    }
    print $fd "100\n";
    sleep 2;
    return undef;
};

my $console = esmith::console->new;

sub doit
{
    my ($self, $console, $db) = @_;

    $console->infobox
        (
         title   => gettext("Starting system services"),
         text    => "\n" .
                    gettext("Please standby while system services are started ..."
),
        );

    system(qw(touch /var/lock/subsys/backup-running));
    system(qw(chown admin /var/lock/subsys/backup-running));
    sleep(6);  # Wait to be certain that all runsv services have been started.
    $console->gauge(\&startup_callback,
        text => '',
        title => 'Starting system services',
        colors => 1,
        no_collapse => 1);
}

#use esmith::console;
#use esmith::ConfigDB;
#esmith::console::startup->new->doit(esmith::console->new(),
#  esmith::ConfigDB->open);
1;
