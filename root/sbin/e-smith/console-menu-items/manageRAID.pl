package esmith::console::manageDiskRedundancy;
use strict;
use warnings;
use esmith::console;
use Locale::gettext;
use Taint::Util;

use Data::Dumper;

use constant DEBUG_MANAGE_RAID => 0;

sub new
{
    my $class = shift;
    my $self = {
		    name => gettext("Manage disk redundancy"),
		    order => 45,
		};
    bless $self, $class;
    return $self;
}

sub name
{
    return $_[0]->{name};
}

sub order
{
    return $_[0]->{order};
}

sub doit
{
    my ($self, $console, $db) = @_;
    my ($rc, $choice);

    use POSIX qw(strftime);

    SCAN:
    my $today = strftime "%A %B %e, %Y %H:%M:%S", localtime;
    my $title = gettext("Disk redundancy status as of") . " " . $today,
    my $text = gettext("Current RAID status:") . "\n\n" . 
        join("", get_raid_status()) . "\n\n";
    my %devices = get_raid_details();

    warn $text if DEBUG_MANAGE_RAID;
    warn "devices: " . Dumper(\%devices) . "\n" if DEBUG_MANAGE_RAID;

    unless (scalar %devices)
    {
        $text = gettext("There are no RAID devices configured");
        ($rc, $choice) = $console->message_page(title => $title, text => $text);
        return;
    }

    # Determine the status of each array
    my @unclean = ();
    my @recovering = ();
    my @failed = ();
    my %used_disks = ();

    for my $dev (keys %devices)
    {
	    $used_disks{$_}++ for (@{$devices{$dev}{UsedDisks}});

        if ($devices{$dev}{FailedDevices} > 0) {
            push @failed, "$dev => " . $devices{$dev}{FailedDevices};
        }

        if ($devices{$dev}{State} =~ /recovering|resync/) {
            push @recovering, "$dev => " . $devices{$dev}{State};
            next;
        }

        next if ($devices{$dev}{State} =~ /^(clean|active)\s*$/);
        push @unclean, "$dev => " . $devices{$dev}{State};
    }

    warn "unclean: @unclean\n" if DEBUG_MANAGE_RAID;
    warn "recovering: @recovering\n" if DEBUG_MANAGE_RAID;
    warn "failed: @failed\n" if DEBUG_MANAGE_RAID;
    warn "used_disks: " . Dumper(\%used_disks) . "\n" if DEBUG_MANAGE_RAID;

    # Check for any spare disks we could add
    my %free_disks = map {$_ => 1} get_disks();
    delete $free_disks{$_} for keys %used_disks;
    warn "free_disks: " . Dumper(\%free_disks) . "\n" if DEBUG_MANAGE_RAID;

    # Report status and return if recovering
    if (scalar @recovering)
    {
        $text .= gettext("A RAID resynchronization is in progress.");
        ($rc, $choice) = $console->message_page(title => $title, text => $text);
        return;
    }

    # Report status and return if arrays are inconsistent
    if ((scalar @unclean && scalar @unclean != scalar keys %devices) || (scalar @failed && scalar @failed != scalar keys %devices))
    {
        $text .= gettext("Only some of the RAID devices are unclean or contain failed disks.") . 
		         "\n\n" .
                 gettext("Manual intervention may be required.") . "\n\n";

        ($rc, $choice) = $console->message_page(title => $title, text => $text);
        return;
    }

    # Report status if arrays are clean and continue if a spare disk is available or there's only one disk in the system
    unless (scalar @unclean || scalar @failed)
    {
        $text .= gettext("All RAID devices are in a clean state.");
        ($rc, $choice) = $console->message_page(title => $title, text => $text);
        return unless scalar keys %free_disks > 0 || scalar keys %used_disks == 1;
    }
    
    # Report status if all arrays are dirty and continue
    if ((scalar @unclean && scalar @unclean == scalar keys %devices) || (scalar @failed && scalar @failed == scalar keys %devices))
    {
        $text .= gettext("All RAID devices are in an unclean state or contain failed disks.");
        ($rc, $choice) = $console->message_page(title => $title, text => $text);
    }

    # Summarise disk assignments
    my $disk_status = gettext("Current disk status:") . "\n\n";
    $disk_status .= gettext("Installed disks") . ": " . 
                    join(" ", get_disks()) . "\n";
    $disk_status .= gettext("Used disks") . ": " . 
                    join(" ", keys %used_disks) . "\n";
    $disk_status .= gettext("Free disks") . ": " . 
                    join(" ", keys %free_disks) . "\n";

    # Spare disk scenarios
    # Scenario 1 - single disk or degraded array with no spare - warn
    if ((scalar @unclean || scalar @failed || scalar keys %used_disks == 1) && scalar keys %free_disks == 0)
    {
        $text = $disk_status . 
            "\n\n" . 
            gettext("To ensure continued redundancy, please shut down, install another drive of the same capacity and then return to this screen.");

        ($rc, $choice) = $console->message_page(title => $title, text => $text);
        return;
    }

    # Scenario 2 - no spares and not degraded so something has gone wrong
    if (scalar keys %free_disks == 0)
    {
        $text = $disk_status . 
            "\n\n" . 
            gettext("Your RAID devices are in an inconsistent state, and no spare drives were detected. You may need to manually remove a failed drive from your arrays using mdadm.");

        ($rc, $choice) = $console->message_page(title => $title, text => $text);
        return;
    }

    # Scenario 3 - multiple spares
    if (scalar keys %free_disks > 1)
    {
        $text = $disk_status . 
            "\n\n" . 
            gettext("Multiple spare drives have been detected. This utility can only add one drive at a time. Please either shut down and remove all but one of your spare drives, or configure your array manually.");

        ($rc, $choice) = $console->message_page(title => $title, text => $text);
        return;
    }

    # Scenario 4 - single spare ready to add
    $text = $disk_status . 
        "\n\n" . 
        gettext("There is an unused disk drive in your system. Do you want to add it to the existing RAID array(s)?") . 
	    "\n\n" .
	    gettext("WARNING: ALL DATA ON THE NEW DISK WILL BE DESTROYED!") .
	    "\n";

    ($rc, $choice) = $console->yesno_page(title => $title, text => $text, defaultno => 1);
    return unless ($rc == 0);

    my @cmd = ("/sbin/e-smith/add_drive_to_raid", "-f", join("", keys %free_disks));
    my $cmd_out = qx( @cmd 2>&1 );
    untaint $cmd_out;

    if ($? == 0) {
        $text = "\nSuccessfully added /dev/" . join("", keys %free_disks) . " to RAID!";
    } else {
        $text = gettext("The command failed:") . " @cmd" .
                "\n\n" . $cmd_out . "\n\n";
    }
    
    ($rc, $choice) = $console->message_page(title => $title, text => $text);
    goto SCAN;
}

sub get_raid_status
{
    die gettext("Couldn't open") . " /proc/mdstat:$!\n"
        unless (open(MDSTAT, "/proc/mdstat"));

    my @mdstat;

    while (<MDSTAT>)
    {
	push @mdstat, "$1\n" if (/(.*\w.*)/);
    }
    close MDSTAT;
    return @mdstat;
}

sub get_raid_details
{
    my @devices = ();

    die gettext("Couldn't call") . " mdadm: $!\n"
        unless open(MDADM, "/sbin/mdadm --detail --scan|");
   
    while (<MDADM>)
    {
        push @devices, $1 if ( m:ARRAY (/dev/md/\w+): ) 
    }
    close MDADM;

    my %devices;

    for my $dev (@devices)
    {
        die gettext("Couldn't call") . " mdadm --detail $dev: $!\n" 
            unless open(MDADM, "/sbin/mdadm --detail $dev|");

        while ( <MDADM> )
        {
            if ( /\s*(.*)\s+:\s+(\d+)\s+\(.*\)\s*/ )
            {
                my ($key, $value) = ($1, $2);
                $key =~ s/\s//g;

		        # Allow for different mdadm output formats for DeviceSize
                $key =~ s/UsedDevSize/DeviceSize/;

                $devices{$dev}{$key} = $value;
            }
            elsif ( /\s*(.*)\s+:\s+(.*)\s*/ )
            {
                my ($key, $value) = ($1, $2);
                $key =~ s/\s//g;
                $devices{$dev}{$key} = $value;
            }

            if ( m:\s+(\d+)\s+(\d+)\s+(\d+).*/dev/([\w\/]+): )
            {
                $devices{$dev}{$1} = $_;
                my $used_disk = $4;
                if (/(rd|ida|cciss|i2o)\//) {
                    $used_disk =~ s/p\d+$//;
                } else {
                    $used_disk =~ s/\d+//;
                }
                push (@{$devices{$dev}{UsedDisks}}, $used_disk);
            }
        }
        close MDADM;
    }

    return %devices;
}

sub get_partitions
{
    die gettext("Couldn't read") . " /proc/partitions: $!\n" 
        unless open (PARTITIONS, "/proc/partitions");

    my %parts;

    while (<PARTITIONS>)
    {
        if ( /\s+(\d+)\s+(\d+)\s+(\d+)\s+([\w\/]+)\s+/ )
        {
            my $name = $4;

            $parts{$name}{major} = $1;
            $parts{$name}{minor} = $2;
            $parts{$name}{blocks} = $3;
        }
    }
    close PARTITIONS;

    return %parts;
}

sub get_disks
{
    my %parts = get_partitions();

    my @disks;

    for (keys %parts)
    {
        push @disks, $_ unless (/[0-9]$/);
        push @disks, $_ if (/(rd|ida|cciss|i2o)\// && ! /p\d+$/);
    }

    return @disks;
}

return new esmith::console::manageDiskRedundancy;
