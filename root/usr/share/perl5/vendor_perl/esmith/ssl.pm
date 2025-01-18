package esmith::ssl;

use strict;
use warnings;
use esmith::ConfigDB;


our @ISA = qw(Exporter);
our @EXPORT = qw( key_exists_good_size cert_exists_good_size cert_is_cert key_is_key related_key_cert SSLproto SSLprotoApache SSLprotoComa SSLprotoHyphen SSLprotoMin SSLprotoLDAP SSLprotoQpsmtpd $smeCiphers $smeSSLprotocol %existingSSLprotos);

my $configdb = esmith::ConfigDB->open_ro or die "Could not open accounts db";
our $SystemName = $configdb->get('SystemName')->value;
our $DomainName = $configdb->get('DomainName')->value;
our $FQDN = "$SystemName.$DomainName";

#default cipher list 
our $smeCiphers = "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256:TLS_AES_128_CCM_SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:ECDH-RSA-AES256-GCM-SHA384:ECDH-ECDSA-AES256-GCM-SHA384:ECDH-RSA-AES256-SHA384:ECDH-ECDSA-AES256-SHA384:ECDH-RSA-AES256-SHA:ECDH-ECDSA-AES256-SHA:!ADH:!SSLv2:!ADH:!aNULL:!MD5:!RC4";
#default protocol list 
# 2024 phase out : TLS 1.1 and 1.0 ; insuficient: SSL 3.0, 2.0 and 1.0
our $smeSSLprotocol = "TLSv1.2 TLSv1.3";

# SSLv2 and SSLv3 are not available in el8 openssl-1.1.1, while -ssl3 still in man page
# it will throw  Option unknown option -ssl3
our %existingSSLprotos=%{ {'SSLv3'=>1, 'TLSv1'=>1, 'TLSv1.1'=>1, 'TLSv1.2'=>1, 'TLSv1.3'=>1}};

=head1 NAME

esmith::ssl - A few tools to help with ssl handling

=head1 SYNOPSIS

    use esmith::ssl;

    my $booleanK=key_exists_good_size;

=head1 DESCRIPTION

This is intended to help playing with installed SSL self-generated certificates and keys.

=head1 Methods


=head2 key_exists_good_size
test key exists, then test key size correct. Obviously it also test that the files is indeed a key
planned to be called in  :
/etc/e-smith/templates/home/e-smith/ssl.crt
/etc/e-smith/templates/home/e-smith/ssl.key

returns 0 if key is missing or wrong size
returns 1 if key exists and key size is correct

=cut

sub key_exists_good_size {
    my $configdb = esmith::ConfigDB->open_ro or die "Could not open accounts db";
    my %modSSL = $configdb->as_hash('modSSL');
    my $KeySize = $modSSL{KeySize} ||'4096';
    my $key = shift || "/home/e-smith/ssl.key/$FQDN.key";
    if ( -f $key ) 
    {
    	#print "$key exists\n";
        # check key size openssl rsa -in /home/e-smith/ssl.key/$host.$domain.key -text -noout | sed -rn "s/Private-Key: \((.*) bit\)/\1/p"
        my $signatureKeySize = `openssl rsa -in  $key -text -noout | grep "Private-Key" | head -1`;
        chomp $signatureKeySize;
        $signatureKeySize =~ s/^.*Private-Key: \((.*) bit.*\)/$1/p;
        if ( $signatureKeySize == $KeySize ) {
		#print "key size is correct ($KeySize)\n";
		# key exists and key size is correct, we can proceed
                return 1;
        }
    } 
    # key is either missing or wrong key size.
    return 0;
}


# test key is key
#openssl rsa -check -in $key

=head2 cert_exists_good_size
# check cert exist
# check cert is cert
# check cert size Public-Key
# openssl rsa -noout -modulus -in domain.key | openssl md5
# openssl x509 -noout -modulus -in domain.crt | openssl md5
=cut

sub cert_exists_good_size {
    my $configdb = esmith::ConfigDB->open_ro or die "Could not open accounts db";
    my %modSSL = $configdb->as_hash('modSSL');
    my $KeySize = $modSSL{KeySize} ||'4096';
    my $crt = shift || "/home/e-smith/ssl.crt/$FQDN.crt";
    if ( -f $crt ) 
    {
	#openssl x509 -text -noout -in /home/e-smith/ssl.crt/$host.$domain.crt| sed -rn "s/Public-Key: \((.*) bit\)/\1/p"
	my $signatureKeySize = `openssl x509 -text -noout -in $crt  | grep "Public-Key" | head -1`;
	chomp $signatureKeySize;
	$signatureKeySize =~ s/^.*Public-Key: \((.*) bit\)/$1/p;
	if ( $signatureKeySize == $KeySize ) {
		#print "$signatureKeySize\n";
		# cert is  correct size and exists, we can proceed.
		# next check key and cert are related
		# next check cert is still valid
		# next check alt name are still the same
		return 1;
	}
    }
    return 0;
}

=head2 cert_is_cert
check if file is really a certificate
=cut

sub cert_is_cert {
    my $crt = shift || "/home/e-smith/ssl.crt/$FQDN.crt";
    if ( -f $crt ) 
    {
        open my $oldout, ">&STDERR";  # "dup" the stdout filehandle
        close STDERR;
	my $exit_code=system("openssl","x509", "-noout", "-in", "$crt");	
        open STDERR, '>&', $oldout;  # restore the dup'ed filehandle to STDOUT
        if ($exit_code==0){
		#print "certificate is a certificate\n";
                return 1;
        }
    }
    return 0;
}

=head2 key_is_key
check if file is really a key
=cut

sub key_is_key {
    my $key = shift || "/home/e-smith/ssl.key/$FQDN.key";
    if ( -f $key )
    {
	open my $oldout, ">&STDERR";  # "dup" the stdout filehandle
	close STDERR;
        my $exit_code=system("openssl","rsa", "-noout", "-in", "$key");
	open STDERR, '>&', $oldout;  # restore the dup'ed filehandle to STDOUT
        if ($exit_code==0){
                #print "key is a key\n";
                return 1;
        }
    }
    return 0;
}

sub related_key_cert {
    my $key = shift || "/home/e-smith/ssl.key/$FQDN.key";
    my $crt = shift || "/home/e-smith/ssl.crt/$FQDN.crt";
    if ( key_is_key($key) and cert_is_cert($crt) )
    { 
	# check the cert and the key are related, if key has been changed, then we need to change the cert
	my $crt_md5 = `openssl x509 -noout -modulus -in $crt | openssl md5`;
	my $key_md5 = `openssl rsa -noout -modulus -in $key | openssl md5`;
	#print "$key_md5 eq $crt_md5\n";
	return 1 if $key_md5 eq $crt_md5;
    }
    return 0;
}

##TODO write sub and migrate those actions from template fragments
# check cert is related to key
# => /etc/e-smith/templates/home/e-smith/ssl.crt 
# check cert domain and alt
# => /etc/e-smith/templates/home/e-smith/ssl.crt 
# check is valid / expiry date
# => /etc/e-smith/templates/home/e-smith/ssl.crt 
###################################

=head2 SSLprotoApache
output a list of allowed protocols with apache format
e.g. -all +TLSv1.2 +TLSv1.3
=cut

sub SSLprotoApache{
 my $protocols = " -all +".join(" +",split(" ",$smeSSLprotocol)) ." ";
 my $configdb = esmith::ConfigDB->open_ro or die "Could not open accounts db";
 my $httpd = $configdb->get('httpd-e-smith');
 # SSLv2 and SSLv3 are not available in el8 openssl-1.1.1, while -ssl3 still referenced
 # it will throw  Option unknown option -ssl3
 #$protocols .= " +SSLv3" if ($httpd->{'SSLv3'} || 'disabled') eq 'enabled';
 #  TODO: a loop using existingSSLprotos
 $protocols .= " +TLSv1" if ($httpd->{'TLSv1'} || 'disabled') eq 'enabled';
 $protocols .= " +TLSv1.1" if ($httpd->{'TLSv1.1'} || 'disabled') eq 'enabled';
 # look closely this is to remove what has been added on first line,
 # hence the minus sign and reverse logic.
 $protocols .= " -TLSv1.2" unless ($httpd->{'TLSv1.2'} || 'enabled') eq 'enabled';
 $protocols .= " -TLSv1.3" unless ($httpd->{'TLSv1.3'} || 'enabled') eq 'enabled';
 return $protocols;
}

=head2 SSLprotoQpsmtpd
output an expected IO::Socket::SSL string to enable 
only the wanted TLS versions
SSLv23:!SSLv2:!SSLv3:!TLSv1:!TLSv1_1
=cut

sub SSLprotoQpsmtpd{
 my $configdb = esmith::ConfigDB->open_ro or die "Could not open accounts db";
 my %qpsmtpd = %{$configdb->get('httpd-e-smith')};
 # SSLv2 and SSLv3 are not available in el8 openssl-1.1.1, while -ssl3 still referenced
 # it will throw  Option unknown option -ssl3
 my $protocols = "SSLv23:!SSLv2:!SSLv3";
 # TODO: a loop using existingSSLprotos and SSLprotoHyphen()
 $protocols .= ':!TLSv1' unless ($qpsmtpd{'TLSv1'} || 'disabled') eq 'enabled';
 $protocols .= ':!TLSv1_1' unless ($qpsmtpd{'TLSv1.1'} || 'disabled') eq 'enabled';
 $protocols .= ':!TLSv1_2' unless ($qpsmtpd{'TLSv1.2'} || 'enabled') eq 'enabled';
 $protocols .= ':!TLSv1_3' unless ($qpsmtpd{'TLSv1.3'} || 'enabled') eq 'enabled';
 return $protocols;
}

=head2 SSLproto
default display of list of protocol. This is how it will be displayed in 
httpd.conf and proftpd.conf
e.g. TLSv1.2 TLSv1.3
=cut

sub SSLproto{
return $smeSSLprotocol;
}

=head2 SSLprotoComa
way to display protocols in Mariadb as a string list separated by coma
e.g. TLSv1.2,TLSv1.3
=cut

sub SSLprotoComa{
my $string = shift || $smeSSLprotocol;
$string =~ s/[ :]/,/g;
return $string;
}

=head2 SSLprotoHyphen
convert TLSv1.2 to TLSv1_2
This is the format required by perl IO::Socket::SSL; and as the result by 
qpsmtpd, uqpsmtpd, sqpsmtpd SME Server services
=cut

sub SSLprotoHyphen {
my $string = shift || $smeSSLprotocol;
$string =~ s/[ ,]/:/g;
$string =~ s/\./_/g;
return $string;
}

=head2 SSLprotoMin
display only the lower protocol, as expected for dovecot
ssl_min_protocol = TLSv1.2
# limit : will not handle all or sslv23 as input
=cut

sub SSLprotoMin{
  my @SSLarray =  split(" ",shift || $smeSSLprotocol);
  my %hash ;
  foreach my $value (@SSLarray) {
    my $toto = $value =~ s/(.*)(\d{1})+$/$2/r;
    # hack for TLS > SSL
    $toto = ($value =~ /^TLS/) ? "2$toto" : "1$toto";
    $hash{$toto}=$value ;
  }
  my @keys_sorted_by_value = sort { $a <=> $b } keys %hash;
  my $lowest_value = $keys_sorted_by_value[0] ;
  return $hash{$lowest_value};
}

=head2 SSLprotoLDAP
convert min protocol suported to LDAP format
TLSProtocolMin          3.3
To require TLS 1.x or higher, set this option to 3.(x+1), e.g., TLSProtocolMin 3.2          would require TLS 1.1.
from $smeSSLprotocol = "TLSv1.2 TLSv1.3";
=cut

sub SSLprotoLDAP{
  # convert to array 
  my @SSLarray =  split(" ",shift || $smeSSLprotocol);
  return "3.0" if  (grep /^SSLv3$/, @SSLarray);
  # TLSv1
  return "3.1" if (grep /^TLSv1$/ , @SSLarray);
  # keep only digit after .
  @SSLarray = grep{ $_ =~ s/(.*)(\d{1})+$/$2/ } @SSLarray;
  # order
  @SSLarray = sort @SSLarray;
  # get lower
  my $num = $SSLarray[0];
  # sum 3.1 + 0.$x
  $num = "0.".$num;
  # return
  $num = $num +3.1;
  return $num;
}
