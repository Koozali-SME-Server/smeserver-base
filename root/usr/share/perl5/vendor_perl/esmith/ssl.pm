package esmith::ssl;

use strict;
use warnings;
use esmith::ConfigDB;


our @ISA = qw(Exporter);
our @EXPORT = qw( key_exists_good_size cert_exists_good_size cert_is_cert key_is_key related_key_cert);

my $configdb = esmith::ConfigDB->open_ro or die "Could not open accounts db";
our $SystemName = $configdb->get('SystemName')->value;
our $DomainName = $configdb->get('DomainName')->value;
our $FQDN = "$SystemName.$DomainName";

# test key size
# test key exists
=head1 NAME

esmith::php - A few tools to help with php-fpm installed versions

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
##TODO migrate those actions from 
# check cert is related to key
# => /etc/e-smith/templates/home/e-smith/ssl.crt 
# check cert domain and alt
# => /etc/e-smith/templates/home/e-smith/ssl.crt 
# check is valid / expiry date
# => /etc/e-smith/templates/home/e-smith/ssl.crt 
###################################
