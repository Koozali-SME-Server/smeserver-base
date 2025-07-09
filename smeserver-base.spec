# $Id: e-smith-base.spec,v 1.153 2023/08/14 18:55:09 jpp Exp $

Summary: smeserver server and gateway - base module
%define name smeserver-base
Name: %{name}
%define version 11.0.0
%define release 34
Version: %{version}
Release: %{release}%{?dist}
License: GPL
Group: Networking/Daemons
Source: %{name}-%{version}.tar.xz
#keeping this one for SME11
# Patch: e-smith-base-5.8.1-bz11772-ellipticcert.patch

BuildRoot: /var/tmp/%{name}-%{version}-%{release}-buildroot
Requires: pwauth
Requires: smeserver-lib >= 11.0.0-7
Requires: server-manager-images, server-manager
Requires: smeserver-formmagick >= 1.4.0-12
Requires: plymouth
Requires: initscripts >= 6.67-1es17
Requires: network-scripts
Requires: rsyslog
Requires: smeserver-daemontools >= 1.7.1-04
Requires: perl(Locale::gettext)
Requires: perl(Crypt::Cracklib)
Requires: perl(Date::Manip)
Requires: perl(Net::IPv4Addr)
Requires: perl(Digest::SHA1)
Requires: perl(Net::Netmask)
Requires: /usr/sbin/irqbalance
Requires: /usr/sbin/smartd
Requires: dbus
Requires: acpid
Requires: bridge-utils
Requires: vconfig
Requires: smeserver-bootloader
Requires: mdadm
Requires: pv
Requires: dhcp-server
Requires: dhcp-client
Requires: diald
Requires: /usr/bin/passwd
Requires: nss-pam-ldapd
Requires: perl-Data-UUID
Requires: kbd
Requires: bash-completion
Requires: smeserver-runit >= 2.6.0-7
Requires: smeserver-php >= 3.0.0-22
Requires: smeserver-yum >= 2.6.0-43 
# daemontools bins in use : 
# /var/service/wan/run.pppoe
Requires: /usr/bin/softlimit 
Obsoletes: nss_ldap < 254
Obsoletes: cpu
Obsoletes: rlinetd, e-smith-mod_ssl
Obsoletes: e-smith-serial-console
Obsoletes: sshell
Obsoletes: e-smith-rp-pppoe
Obsoletes: e-smith-pptpd
Obsoletes: e-smith-dynamicdns-yi
Obsoletes: e-smith-dynamicdns-tzo
Obsoletes: e-smith-dynamicdns-dyndns.org
Obsoletes: e-smith-dynamicdns-dyndns
BuildRequires: perl, perl(Test::Inline) >= 0.12
BuildRequires: smeserver-devtools >= 1.13.1-03
BuildRequires: gettext
Requires: gdisk
Requires: ppp
Requires: rp-pppoe
# pam autoblock 
Requires: pam_abl 
# isdn wan connection (ippp)
Requires: isdn4k-utils
%define dbfiles accounts configuration domains hosts networks
AutoReqProv: no

Provides: e-smith-base
%description
smeserver server and gateway software - base module.

%prep
%setup

%build

LEXICONS=$(find root/etc/e-smith/web/functions -type f| grep -v CVS)

for lexicon in $LEXICONS
do
    /sbin/e-smith/validate-lexicon $lexicon
done

/sbin/e-smith/generate-lexicons

xgettext -L perl -o root/usr/share/locale/en_US/LC_MESSAGES/server-console.po root/sbin/e-smith/console.pl

perl createlinks
/sbin/e-smith/buildtests 10e-smith-base

gcc -g -o root/sbin/e-smith/console console_wrapper.c

# Force creation of potentially empty directories
mkdir -p root/etc/e-smith/web/panels/password/cgi-bin
ln -s ../../../functions/wrapper root/etc/e-smith/web/panels/password/cgi-bin/userpassword

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc/selinux
(cd root   ; find . -depth -print | cpio -dump $RPM_BUILD_ROOT)
/sbin/e-smith/genfilelist $RPM_BUILD_ROOT \
    --file /sbin/e-smith/systemd/network-pre 'attr(0554,root,root)' \
    --file /sbin/e-smith/systemd/mdmonitor-pre 'attr(0554,root,root)' \
    --file /sbin/e-smith/systemd/rsyslog-pre 'attr(0554,root,root)' \
    --file /etc/cron.daily/conf-mod_ssl 'attr(0544,root,root)' \
    --file /etc/dhcp/dhclient-exit-hooks 'attr(0755,root,root)' \
    --dir /var/log/dhcpd 'attr(2750,smelog,smelog)' \
    --dir /etc/e-smith/pam 'attr(0700,root,root)' \
    --dir /home/e-smith/ssl.key 'attr(0700,root,root)' \
    --dir /home/e-smith/ssl.crt 'attr(0700,root,root)' \
    --dir /home/e-smith/ssl.pem 'attr(0700,root,root)' \
    --dir /var/service/wan 'attr(1755,root,root)' \
    --file /var/service/wan/run 'attr(0750,root,root)' \
    --file /var/service/wan/run.dhclient 'attr(0750,root,root)' \
    --file /var/service/wan/run.pppoe 'attr(0750,root,root)' \
    --file /var/service/wan/run.static 'attr(0750,root,root)' \
    --file /var/service/wan/run.dialup 'attr(0750,root,root)' \
    --file /var/service/wan/run.disabled 'attr(0750,root,root)' \
    --dir /var/log/wan 'attr(2750,smelog,smelog)' \
    --dir /var/log/ippp 'attr(2750,smelog,smelog)' \
    --dir /etc/e-smith/skel/user/.ssh 'attr(0700,root,root)' \
    --file /etc/sysconfig/modules/dummy.modules 'attr(0755,root,root)' \
    --dir /etc/selinux 'attr(0755,root,root)' \
    | sed -e '/\/etc\/dhcp$/d'  \
    > %{name}-%{version}-%{release}-filelist

mkdir -p $RPM_BUILD_ROOT/home/e-smith/db
for file in %{dbfiles}
do
    # Create ghost file for rpm
    touch $RPM_BUILD_ROOT/home/e-smith/db/$file
    echo "%config(noreplace) %attr(0640,root,admin) /home/e-smith/db/$file" \
        >> %{name}-%{version}-%{release}-filelist
done
echo "%doc COPYING"          >> %{name}-%{version}-%{release}-filelist

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}-%{version}-%{release}-filelist
%defattr(-,root,root)

%pre
/sbin/e-smith/create-system-user smelastsys 2999 \
    'sme last system user marker' /tmp /bin/false


exit 0

%post
LEXICONS=$(find /etc/e-smith/locale/*/etc/e-smith/web/panels/password/cgi-bin/userpassword -type f 2>/dev/null)

for lexicon in $LEXICONS
do
    if [ -f $lexicon ]
    then
        cd $(dirname "$lexicon")
        mv ./userpassword ../../../functions
    fi
done

if [ -d "/var/service/dhcpd" ]; then
        rm -rf /var/service/dhcpd
fi
if [ -d "/var/service/raidmonitor" ]; then
        rm -rf /var/service/raidmonitor
fi
if [ -d "/var/service/local" ]; then
        rm -rf /var/service/local
fi


%changelog
* Wed Jul 09 2025 John Crisp <jcrisp@safeandsoundit.co.uk> 11.0.0-34.sme
- fix hardcoded rp-pppoe.so location - Thanks Nestor [SME: 13074]

* Thu Jun 12 2025 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-33.sme
- fix autorenew of self-signed certificate [SME: 12218]
  strips unsupported characters, use utf8 encoding

* Thu Jun 05 2025 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-32.sme
- Replicate user accounts to samba Active Directory [SME: 12799]

* Sun Mar 16 2025 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-31.sme
- handle dh params with template [SME: 12826]
 TODO timer and event
- foolproofing dummy.module

* Thu Mar 06 2025 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-30.sme
- systemd unit for ippp [SME: 12876]
- systemd unit for wan [SME: 12875]
- improve networking service unit [SME: 12541]

* Wed Mar 05 2025 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-29.sme
- change key type from service to configuration [SME: 11367]

* Thu Feb 20 2025 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-28.sme
- clean sme-server.target [SME: 12931]

* Sun Feb 16 2025 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-27.sme
- fix missing allowed shell for login [SME: 12926]

* Wed Feb 12 2025 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-26.sme
- add pam_abl requirement [SME: 12914]
- add isdn4k-utils requirement for ippp isdn connections [SME: 12909]
- remove pam_tally as deprecated in favor of pam_faillock [SME: 12913]

* Tue Feb 04 2025 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-25.sme
- fix boot ordering cycle [SME: 12902]

* Sun Jan 26 2025 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-24.sme
- ippp and wan requires daemontools bins [SME: 12566]

* Sat Jan 18 2025 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-23.sme
- handle all ssl ciphers and protocol in one place esmith::ssl [SME: 12827]
  this will allow to sync all service default protocol and ciphers
  in one place.

* Fri Jan 03 2025 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-21.sme
- improve support of  systemd service with instance service@instance.service [SME: 12859]

* Thu Jan 02 2025 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-20.sme
- Primary default to SSL required and redirect [SME: 12858]
- cleanup remove primary=system [SME: 8268]

* Tue Dec 31 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-19.sme
- fix www removed from shared on group creation [SME: 12848]

* Mon Dec 23 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-18.sme
- add vlan support on External Interface [SME: 12677]
- fix typo [SME: 12763] 

* Mon Dec 23 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-16.sme
-  add kernel module support for rp-pppoe plugin [SME: 12678]
   will allow faster fiber connexion when using multiple queue interface (RSS)
   set-gateway-ip will propagate both wan and diald ip
   run.pppoe call an interface

* Sat Dec 21 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-15.sme
- fix use of passwd command when ldap auth enabled [SME: 6453]
- delete spool file only if exists to avoid error [SME: 12763]

* Mon Sep 23 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-14.sme
- fix result variable not initialized [SME: 12663]

* Sun Sep 22 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-13.sme
- fix mail spool perms [SME: 12654]
- fix motd noise related to cockpit [SME: 12575]
- fix /run vs /var/run temps dir noise [SME: 12639]

* Wed Aug 14 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-12.sme
- fix 3 regressions from SME10 [SME: 12654]
  fix www missing from shared and few groups [SME: 12146]
  fix group deletion leaves mail spool file [SME: 12431]
  fix path to /etc/systemd for seeking service files [SME: 12421]

* Tue Aug 13 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-11.sme
- fix new systemd.log does not fill after log rotate [SME: 12688]

* Wed May 15 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-10.sme
- fix user@0.service failed to start [SME: 12568]
- stop loging in audit crond success
- drop cpu and use esmith:util::ldap [SME: 12663]

* Wed Apr 17 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-9.sme
- fix self-signed cert renewd when not necessary [SME: 12606]

* Tue Apr 16 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-8.sme
- add requirement for ppp [SME: 12622]
- add requirement for rp-pppoe [SME: 12628]
- enable modprobe dummy and bond [SME: 12627] 

* Sat Apr 13 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-7.sme
- fix init-accounts [SME: 12546]

* Thu Apr 04 2024 Brian Read <brianr@koozali.org> 11.0.0-6.sme
- Update createlinks to create smeserver-package-update event[SME: 12579]

* Thu Apr 04 2024 Brian Read <brianr@koozali.org> 11.0.0-5.sme
- Set license file to GPL2.0  [SME: 12577]

* Tue Mar 26 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-4.sme
- fix networking [SME: 12541]
- require rsyslog [SME: 12544]
- remove unsupported rsyslog option -c [SME: 12545]
- remove duplicate entry logrotate for btmp and wtmp [SME: 12547]
- rework systemd-default script (error and smartmatches) [SME: 12543]  
- fix self signed cert templates [SME: 12551]

* Sat Mar 23 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-3.sme
- fix requirement for el8 SME11 [SME: 12521]

* Sat Mar 23 2024 Brian Read <brianr@koozali.org>11.0.0-2.sme
- Change Requires: e-smith- to Requires:smeserver-

* Sat Mar 23 2024 Brian Read <brianr@koozali.org>11.0.0-1.sme
- Update Release and Version to base version and 1st release for SME11 [SME: 12518]

* Thu Mar 14 2024 Jean-Philippe Pialasse <jpp@koozali.org> 5.8.1-33.sme
- drop rssh support and requirement [SME: 12509]

* Tue Mar 12 2024 Jean-Philippe Pialasse <jpp@koozali.org> 5.8.1-32.sme
- add gcc -g flag to allow el8 build

* Mon Mar 11 2024 rename-e-smith-pkg.sh by Trevor Batley <trevor@batley.id.au> 5.8.1-31.sme
- Rename to smeserver-base [SME: 12359]

* Thu Oct 26 2023 cvs2git.sh aka Brian Read <brianr@koozali.org> 5.8.1-30.sme
- Roll up patches and move to git repo [SME: 12338]

* Thu Oct 26 2023 BogusDateBot
- Eliminated rpmbuild "bogus date" warnings due to inconsistent weekday,
  by assuming the date is correct and changing the weekday.

* Mon Aug 14 2023 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-29.sme
- fix systemd loop during bootstrap console restore [SME: 12335]

* Thu Feb 09 2023 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-28.sme
- option to expand the prunepaths variable for locate [SME: 11518]

* Wed Feb 08 2023 Zsolt Vasarhelyi <vasarhelyizsolt@hotmail.com> 5.8.1-27.sme
- Logging stops to messages - imjournal: too many open files [SME: 12304]

* Mon Feb 06 2023 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-26.sme
- ldap not available at bootstrap [SME: 12178]

* Sun Feb 05 2023 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-25.sme
- fix raidmonitor not starting [SME: 12182]

* Thu Dec 29 2022 Brianb Read <brianr@bjsystems.co.uk> 5.8.1-24.sme
-  DHCPD set DNSServers [SME: 12295]

* Mon Dec 12 2022 Terry Fage <terry@fage.id.au> 5.8.1-23.sme
-  DHCP Not working since last updates [SME: 12257]

* Sun Dec 04 2022 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-22.sme
- do not launch bootstrap-runlevel7 if no sysvinit service available [SME: 12253]

* Thu Nov 24 2022 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-21.sme
- fix typo [SME: 12190]

* Tue Nov 22 2022 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-20.sme
- expand dropin for dhcp unit [SME: 12183]
- add PartOf=networking.service to wan.service [SME: 12195]
- reduce imjournal rate-limiting  [SME: 12175]

* Tue Nov 22 2022 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-19.sme
- fix smartd not running because config path has changed [SME: 12190]
- do not check disk is in standby

* Fri Sep 09 2022 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-18.sme
- fix comparison operator for logrotate fix [SME: 11950]
  changing also restart to reload [SME: 12164]

* Fri Jul 29 2022 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-17.sme
- no new self signed cert when adding/removing non self hosts [SME: 12130]

* Sun Jun 19 2022 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-16.sme
- fix /dev/log not being recreated [SME: 12073]

* Sun Apr 17 2022 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-15.sme
- add rsshusers group to ldap and update it [SME: 11956]

* Sat Apr 16 2022 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-14.sme
- fix symlinks preventing log rotation [SME: 11950]

* Sat Apr 16 2022 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-12.sme
- remove immark module to reduce messages log activity [SME: 11813]

* Fri Apr 15 2022 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-11.sme
- fix logs not rotated before 100M (size maxsize) [SME: 10484]
- reduce systemd noise in messages [SME: 11813]

* Mon Apr 04 2022 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-10.sme
- fix dhcp address not propagated [SME: 11930]

* Thu Feb 17 2022 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-8.sme
- make rsyslog listen journald which listen /dev/log [SME: 11813]
  template for /etc/systemd/journald.conf
- properly configure /etc/logrotate.conf [SME: 10484]
  template for /etc/logrotate.conf
  use of size to limit max size of file and rotate earlier
- drop e-smith logrotate actions creating dangling links [SME: 946]

* Mon Dec 20 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-6.sme
- make journald log permanent by creating /var/log/journal [SME: 11795]

* Tue Nov 23 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-4.sme
- allow group-modify-unix on update event [SME: 11766]

* Mon Nov 15 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-3.sme
- fix typo in last patch [SME: 11722]

* Wed Oct 27 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-2.sme
- add support for systemd service with instance service@instance.service [SME: 11722]

* Sun Jun 06 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.1-1.sme
- add local domains in self signed cert alt subjects [SME: 11624]
  add local hosts in self signed cert alt subjects 
  modSSL property to disable hosts domains addition : AddDomains AddHosts
  default is enabled when empty

* Fri Jun 04 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-99.sme
- fix missing export [SME: 11620]

* Tue Jun 01 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-97.sme
- fix issue with adding new user to the ldap db [SME: 11607]

* Tue Jun 01 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-96.sme
- always renew self signed certificate [SME: 11552]
  update key / crt if not signed with the right key size
  default to self signed if custom cert and key are not files or not rigth type
  add perl module to help handle certificates and keys
  TODO: check if both key and cert are related, if not default to self signed

* Wed Apr 21 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-95.sme
- fix openssl.conf not generated when openldap field are empty [SME: 11569]

* Thu Apr 08 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-94.sme
- fix missing path to systemctl for add-wants [SME: 11537]

* Tue Mar 30 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-93.sme
- merge dhcpdmanager custom template fragments with core [SME: 10657]
- remove templates-custom previously owned by a contrib [SME: 11508]
  they got migrated as part as normal backup restore

* Sun Mar 21 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-92.sme
- fix masq failing on initial boot [SME: 11479]

* Fri Mar 19 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-91.sme
- removing weekly cron for ddns update, targeted script has been removed [SME: 11470]

* Thu Mar 18 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-90.sme
- revert e-smith-service file [SME: 9692]
- add systemctl wrapper [SME: 11345]

* Tue Mar 16 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-89.sme
- clean rsyslog syntax for dhcpd [SME: 11422]

* Tue Mar 16 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-88.sme
- cleanup /etc/rc.d and /var/service [SME: 9692]

* Wed Mar 03 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-87.sme
- remove klogd references [SME: 11363]
- restore part of pptp code and move to generik vpn entry [SME: 11374]

* Wed Mar 03 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-85.sme
- drop dyndns core support [SME: 11415]

* Thu Feb 18 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-84.sme
- fix enabled service not started on reboot [SME: 11355]
  unless a power outage, as long as you reboot, halt or shutdown systemd will
  be in sync
- fix console::startup run twice [SME: 11358 ]
- improve run order in systemd-default [SME: 11356]

* Wed Feb 17 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-83.sme
- fix uninitialized value during post-install [SME: 11350]

* Sun Feb 14 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-81.sme
- fix user with rssh shell need to be member of rsshusers group [SME: 9155]

* Fri Feb 12 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-80.sme
- add missing  /sbin/e-smith/bootstrap-runlevel7 [SME: 11318]

* Mon Jan 11 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-79.sme
- fix typo for isolate [SME: 11246]

* Mon Jan 11 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-78.sme
- separate bootstrap-console from run level service launch [SME: 11318]

* Fri Jan 08 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-75.sme
- only run isolate if sme-server.target is not active [SME: 11246]
- update system-preset usr/lib file [SME: 10958]

* Wed Jan 06 2021 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-72.sme
- fix loss of httpd basic auth [SME: 11309]

* Fri Dec 25 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-71.sme
- fix services starting when they are in Wants= for sme-server.target and preset disabled [SME: 11247]

* Wed Dec 23 2020 Chris Sansom-Ninnes <chris@sansom.ninnes.net> 5.8.0-70.sme
- rewrite of manageRAID.pl and add_drive_to_raid for SME10 [SME:10918]
- added gdisk as a dependency to support GPT systems

* Fri Dec 11 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-69.sme
- fix modSSL key crt and keychain files really exist [SME: 11252]
- add ldap.init as exception for preset

* Fri Dec 11 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-68.sme
- fix init-accounts [SME: 9642]

* Fri Dec 11 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-67.sme
- validate modSSL key crt and keychain files really exist [SME: 11252]
  if not we use self generated

* Fri Dec 11 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-66.sme
- drop pptpd support [SME: 11250]

* Wed Dec 09 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-65.sme
- add bash-completion [SME: 11244]
- improve  local service to systemd [SME: 11119]
  now run rc.local file as part of the event

* Wed Dec 09 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-64.sme
- move local service to systemd [SME: 11119]
  make it run /etc/rc.d/rc.local
  cleaning /var/service/syslog still there

* Sat Dec 05 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-63.sme
- workaround drop-in install section ignored by systemctl preset [SME: 11231]
  some cleanup

* Thu Dec 03 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-61.sme
- remove S95reset-unsavedflag [SME: 11229]
- add exclusion for lpd [SME: 11006]

* Thu Dec 03 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-60.sme
- execute systemd-reload before service adjust in events [SME: 11228]

* Tue Dec 01 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-59.sme
- fix ExecStart for raidmonitor [SME: 11094]

* Sun Nov 29 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-58.sme
- fix permission for /sbin/e-smith/systemd/mdmonitor-pre [SME: 11094]

* Wed Nov 25 2020 Chris Sansom-Ninnes <chris@sansom.ninnes.net> 5.8.0-57.sme
- Don't ask for confirmation to save changes on first install configuration [SME: 11193]

* Wed Nov 25 2020 Chris Sansom-Ninnes <chris@sansom.ninnes.net> 5.8.0-56.sme
- Fix RAID detection regex for disk redundancy screen [SME: 10918]

* Wed Nov 18 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-55.sme
- add Install part of systemd unit [SME: 11100]

* Tue Nov 17 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-54.sme
- move dhcpd to systemd [SME: 11100]
- get dhcpd log out of message [SME: 2408]
  also configure logrotate for /var/log/dhcpd/dhcpd.log and /var/log/dhcpd/current

* Tue Nov 17 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-53.sme
- reverte previous changes for service2adjust and util.pm [SME: 11177]
  files are owned by e-smith-lib

* Mon Nov 16 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-52.sme
- allow more systemctl controls [SME: 11177]
  convert unrecognized signals from service2adjust in events for systemd
  handle unsupervised services the same way supervised were in adjust-services
  make service-status only log when service disabled and not fail it

* Sat Nov 14 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-51.sme
- add template for /etc/systemd/system-preset/49koozali.preset  [SME: 11174]
  this will help systemd integration in enabling and disabling services
  remove wan link

* Wed Nov 11 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-50.sme
- move raidmonitor to systemd [SME: 11094]

* Tue Nov 10 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-49.sme
- move network service to systemd [SME: 11090]
- move wan service to systemd [SME: 11091]

* Wed Sep 30 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-48.sme
- create e-smith-base-update event [SME: 11012]
- create sme-server.target [SME: 10957]
  make sme-server.target default target
  change default target on  signal-event post-upgrade, post-install, e-smith-base-update
  requires update or smeserver-php and e-smith-runit
- add an executable to check if service is enabled in e-smith db

* Sat Jun 27 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-47.sme
- validate submask on remote access panel [SME: 6536]
  accept netmask bit and convert it
- validate subnet mask on local network panel [SME: 10974]
  accept netmask bit and convert it

* Tue Jun 23 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-45.sme
- remove info.txt [SME: 9590]

* Sun May 24 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-44.sme
- wildcard self-signed certificate [SME: 8156]
  * ip in self-signed certificate
  * subject altname in self-signed certificate
  * ability to define Country code and State using 
    modSSL{Country} and modSSL{State} properties
  * /etc/openssl.conf is used now and templated for self-signed certificate

* Sat May 23 2020 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-43.sme
- enable smartd for existing installation [SME: 5890]

* Sun May 17 2020 Chris Sansom-Ninnes <chris@sansom.ninnes.net> 5.8.0-42.sme
- Enable smartd by default [SME: 5890]
- Credit to Chris Burnat

* Wed Dec 18 2019 Michel Begue <mab974@gmail.com> 5.8.0-41.sme
- Add a link to manager C wrapper to execute userpassword's cgi to replace perl-suid [SME: 9677]

* Fri Nov 22 2019 John Crisp <jcrisp@safeandsoundit.co.uk> 5.8.0-40.sme
- fix SystemName [SME: 8876]

* Tue Jan 22 2019 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-39.sme
- modify the default city and company [SME: 10715]

* Tue Feb 13 2018 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-38.sme
- cleaning xinetd.conf fragment out of the package [SME: 10219]

* Wed Nov 15 2017 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-37.sme
- revert previous change - wrong package

* Tue Nov 14 2017 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-36.sme
- added post transaction rule for ntp [SME: 10190]
- thank you to Stefano Zamboni for this work

* Thu May 4 2017 Daniel Berteaud <daniel@firewall-services.com> 5.8.0-35.sme
- Expand route-bond0 when nic bonding is enabled [SME: 10272]

* Sat Apr 15 2017 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-34.sme
- improve regex to catch local [SME: 9724]

* Wed Apr 12 2017 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-33.sme
- change smtpd to qpsmtpd for default service access [SME: 9478]

* Mon Feb 27 2017 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-32.sme
- add translation links for manager to most language variations we support [SME: 11121]

* Fri Feb 17 2017 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-31.sme
- prevent restoration from being called on regular and post-upgrade reboot [SME: 9550]
- console restoration can be launched again from console

* Thu Feb 9 2017 Daniel Berteaud <daniel@firewall-services.com> 5.8.0-30.sme
- Use ip route syntax to define routes to local network [SME: 10083]

* Tue Sep 6 2016 Daniel Berteaud <daniel@firewall-services.com> 5.8.0-29.sme
- Allow /32 masks on the external interface, in which case we don't
  check if the gateway is on the correct network) [SME: 9610]

* Thu Aug 04 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-28.sme
- fix config db locale property [SME: 9724]

* Sat Jul 23 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-27.sme
- adapt e-smith service command to systemd [SME: 9672]

* Fri Jul 22 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-26.sme
- add systemd skip redirect to e-smith-service  [SME: 9688]

* Thu Jul 21 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-25.sme
- fix broken link /etc/init.d/supervise/local link [SME: 9687]

* Mon Jul 18 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-22.sme
- fix mysqld to mariadb  [SME: 9438]

* Sat Jul 16 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-21.sme
- fix missing path to chkconfig [SME: 9641]

* Thu Jul 14 2016 stephane de Labrusse <stephdl@de-labrusse.fr> 5.8.0-20.sme
- Fix deprecated syntax '*' in rsyslog [SME: 9398]
- Added e-smith-base-5.8.0.bz9398.DeprecatedRsyslogSyntax.patch

* Mon Jul 4 2016 stephane de Labrusse <stephdl@de-labrusse.fr> 5.8.0-19.sme
- Set the hostname by hostnamectl [SME: 9631]
- Stefano Zamboni <zamboni@mind-at-work.it>

* Sun Jun 12 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-18.sme
- fix Lang and keyboard layout configured are not used [SME: 9539]

* Thu Jun 2 2016 Daniel Berteaud <daniel@firewall-services.com> 5.8.0-17.sme
- Fix display of email forward fields since smtpd entry has been merged
  qpsmtpd [SME: 9552]

* Sun May 29 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-16.sme
- Allow bootstrap to start services after post-install configuration [SME: 9530]

* Thu May 12 2016 Daniel Berteaud <daniel@firewall-services.com> 5.8.0-15.sme
- Use a C wrapper for the console to replace perl-suid [SME: 9393]

* Wed Apr 13 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-14.sme
- fix password not asked after signal-event post-install [SME: 9445]

* Wed Apr 13 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-13.sme
- only start services on regular boot  [SME: 9436]

* Tue Apr 12 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-12.sme
- fix getting locale for db configuration  [SME: 9378]

* Mon Apr 11 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-11.sme
- rearange startup [SME: 9352]
- let systemd handle following unsupervised services:
- bootstrap-console, rsyslog, irqbalance, crond, acpid, smartd
- disable from systemd services whith link in rc7.d
- let bootstrap-console run at every reboot and handle surpevised services startup

* Mon Apr 11 2016 Daniel Berteaud <daniel@firewall-services.com> 5.8.0-9.sme
- Remove ctrlaltdel service entry [SME: 9437]

* Mon Apr 11 2016 Daniel Berteaud <daniel@firewall-services.com> 5.8.0-8.sme
- Remove obsolete services [SME: 9420]

* Tue Mar 29 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-7.sme
- added requires dhcp [SME: 9392]

* Wed Mar 23 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-6.sme
- add Requires perl(Digest::SHA1) for console [SME: 9372]

* Fri Mar 18 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-5.sme
- fix conflict  perl-Data-UUID vs uuid-perl [SME: 9344]

* Fri Mar 18 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-3.sme
- remove cpuspeed Requires and support [SME: 9337]
- remove pam_abl Requires [SME: 9341]

* Fri Mar 18 2016 Jean-Philippe Pialasse <tests@pialasse.com> 5.8.0-2.sme
- Remove Requires: hal [SME: 9342]
- Eliminated rpmbuild "bogus date" warnings due to inconsistent weekday,
  by assuming the date is correct and changing the weekday.
  Sat Dec 25 2005 --> Sat Dec 24 2005 or Sun Dec 25 2005 or Sat Dec 31 2005 or ....
  Mon Feb 21 2006 --> Mon Feb 20 2006 or Tue Feb 21 2006 or Mon Feb 27 2006 or ....
  Sat Mar 07 2008 --> Sat Mar 01 2008 or Fri Mar 07 2008 or Sat Mar 08 2008 or ....
  Sat Mar 10 2008 --> Sat Mar 08 2008 or Mon Mar 10 2008 or Sat Mar 15 2008 or ....
  Mon Apr 21 2013 --> Mon Apr 15 2013 or Sun Apr 21 2013 or Mon Apr 22 2013 or ....
  Tue Sep 30 2015 --> Tue Sep 29 2015 or Wed Sep 30 2015 or Tue Oct 06 2015 or ....

* Fri Feb 5 2016 Daniel Berteaud <daniel@firewall-services.com> 5.8.0-1.sme
- Roll new stream for sme10

* Sun Jan 31 2016 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-28.sme
- Add a column to display forwarding address [SME: 9174]

* Sun Jan 31 2016 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-27.sme
- Correctly display http URL to the server-manager in the console [SME: 9163]

* Sun Jan 17 2016 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-26.sme
- Fire ssl-update event when default cert is renewed [SME: 2257]

* Sun Jan 17 2016 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-25.sme
- Expand /home/e-smith/ssl.pem/pem during ssl-update [SME: 9152]

* Wed Sep 30 2015 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-24.sme
  Tue Sep 30 2015 --> Tue Sep 29 2015 or Wed Sep 30 2015 or Tue Oct 06 2015 or ....
- Update /etc/mime.types templates [SME: 9078]

* Mon Aug 24 2015 Charlie Brady <charlie_brady@mitel.com> 5.6.0-23.sme
- Use sha256 algorithm for signature of SSL cert. [SME: 8615]

* Thu Jun 25 2015 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-22.sme
- Fix including /etc/selinux directory [SME: 8954]

* Thu Jun 25 2015 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-21.sme
- Add templates for /etc/selinux/config [SME: 8954]

* Thu Jun 11 2015 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-20.sme
- Add dummy NIC support as InternalInterface [SME: 7200]

* Tue Mar 31 2015 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-19.sme
- Only fire the ip-change event when IP is assigned to WAN nic
  (Code by Charlie Brady and John Crisp) [SME: 8896]

* Tue Mar 31 2015 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-18.sme
- Only reset service access when switching to or from private server mode
  (Code by Charlie Brady) [SME: 8879]

* Sun Jan 11 2015 Stephane de Labrusse <stephdl@de-labrusse.fr> 5.6.0-17.sme
- When quiting the console app with unsaved changes set the default selected 
- answer to NO  Hsing-Foo Wang <hsingfoo@gmail.com> [SME: 8616]

* Tue Jan 6 2015 Stephane de Labrusse <stephdl@de-labrusse.fr> 5.6.0-16.sme
- Added a comment to specify the real configuration file of dhcpd [SME: 8386]

* Sat Jan 3 2015 Stephane de Labrusse <stephdl@de-labrusse.fr> 5.6.0-15.sme
- Modified the patch of daniel e-smith-base-5.6.0-ensure_apache_alias_www.patch
- Ensure www group exists and that apache is an alias of www [SME: 8549]

* Sun Nov 2 2014 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-13.sme
- Ensure www group exists and that apache is an alias of www [SME: 8549]

* Sun Nov 2 2014 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-12.sme
- Check were running runlevel 4, not 7 in service wrapper [SME: 8637]

* Sun Sep 21 2014 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-11.sme
- Correctly update NIC configuration on single NIC systems [SME: 8561]

* Wed Sep 10 2014 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-10.sme
- Symlink udev-post service in rc7 [SME: 8542]

* Fri Jul 25 2014 Daniel Berteaud <daniel@firewall-services.com> 5.6.0-9.sme
- Fix PPPoE after a post-upgrade [SME: 8493]

* Thu Jul 3 2014 Ian Wells <esmith@wellsi.com> 5.6.0-8.sme
- Remove dependency on microcode_ctl [SME: 8468]

* Sun May 11 2014 stephane de Labrusse <stephdl@de-labrusse.fr> 5.6.0-7.sme
- Prevent emailing about the normal, weekly, checks of RAID arrays, by Mark Casey
- [SME: 7748]

* Tue May 06 2014 stephane de Labrusse <stephdl@de-labrusse.fr> 5.6.0-6.sme
- remove /etc/e-smith/templates/etc/crontab/10runparts for anacron compatibility 
- [SME: 8364]

* Wed Apr 23 2014 stephane de Labrusse <stephdl@de-labrusse.fr> 5.6.0-5.sme
- Add a verification in the console of number of pptp clients against ip allowed in dhcpd
- [SME: 8312]

* Sun Apr 6 2014 stephane de Labrusse <stephdl@de-labrusse.fr> 5.6.0-4.sme
- Add a verification in remoteaccess panel of number of pptp clients against ip allowed in dhcpd
- [SME: 8312]

* Sat Apr 5 2014 Ian Wells <esmith@wellsi.com> 5.6.0-3.sme
- Ensure console is run with taint checking [SME: 8311]
- Non-functional perl::Critic changes.

* Sun Mar 23 2014 Ian Wells <esmith@wellsi.com> 5.6.0-2.sme
- Roll new stream to really remove obsolete images [SME: 7962] 

* Sun Mar 23 2014 Ian Wells <esmith@wellsi.com> 5.6.0-1.sme
- Roll new stream to remove obsolete images [SME: 7962] 

* Thu Mar 20 2014 Ian Wells <esmith@wellsi.com> 5.4.0-62.sme
- Move console backup to e-smith-backup [SME: 3324]

* Sun Mar 16 2014 Ian Wells <esmith@wellsi.com> 5.4.0-61.sme
- Remove support.pl from e-smith-base and move to smeserver-support [SME: 8264]

* Sat Mar 15 2014 Ian Wells <esmith@wellsi.com> 5.4.0-60.sme
- Console restore should reboot [SME: 8259]

* Sat Mar 8 2014 Ian Wells <esmith@wellsi.com> 5.4.0-59.sme
- Boostrap console should only offer restore if no password set [SME: 8259]

* Thu Mar 6 2014 Ian Wells <esmith@wellsi.com> 5.4.0-58.sme
- Add restore backup as a console item for freshly installed servers [SME: 8259]
- Non-code changes to perform_restore.pm

* Sun Feb 16 2014 Ian Wells <esmith@wellsi.com> 5.4.0-57.sme
- Refer to removable media not CDROM in console restore [SME: 8214]

* Tue Jan 28 2014 Ian Wells <esmith@wellsi.com> 5.4.0-56.sme
- Remove insecure SSL ciphers [SME: 8138]

* Sun Dec 15 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-55.sme
- Restart rsyslog in logrotate event [SME: 8065]

* Sun Dec 15 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-54.sme
- Set smb ServerName if unset (patch from Ian Wells) [SME: 8030]

* Mon Dec 9 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-53.sme
- Don't reload init in bootstrap-console-save and console-save [SME: 8050]

* Mon Dec 9 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-52.sme
- Re-add missing templates metadata for bond0 [SME: 7990]

* Sat Nov 30 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-51.sme
- Load the bonding module if NIC bonding is enabled [SME: 7996]

* Sat Nov 30 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-50.sme
- Define the udev-post service in the DB [SME: 7992]

* Sat Nov 30 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-49.sme
- Remove the "swap interface" feature [SME: 7993]

* Sat Nov 30 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-48.sme
- Do not hardcode NIC names to eth0 and eth1 [SME: 7990]
- Remove obsolete VLAN code [SME: 7994]

* Sat Nov 30 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-47.sme
- Remove HWAddress prop from interfaces [SME: 7991]

* Thu Nov 14 2013 Chris Burnat <devlist@burnat.com> 5.4.0-46.sme
- Fix add_new_disk_to_raid1 (codes by Charlie Brady - patch by Terje Edseth)
 [SME: 7960]

* Wed Oct 30 2013 Charlie Brady <charlie_brady@mitel.com> 5.4.0-45.sme
- Fix parsing issues with "manage RAID" menu option in the console.
  [SME: 7953]

* Mon Sep 30 2013 John H. Bennett III <bennettj@johnbennettservices.com> 5.4.0-44.sme
- Patch to correct issue with not being able to access a password protected
   ibay [SME: 7794]

* Sun Jul 7 2013 Ian Wells <esmith@wellsi.com> 5.4.0-43.sme
- Improve text in console backup for success and failure [SME: 7770]

* Fri Jul 5 2013 Ian Wells <esmith@wellsi.com> 5.4.0-42.sme
- Console USB Backup, allow user setting of compression level [SME: 7745]
  Compression level of the console backup is now -6 by default

* Fri Jul 5 2013 Ian Wells <esmith@wellsi.com> 5.4.0-41.sme
- Update ServerName (Samba netbios name) when SystemName is updated [SME: 7746]

* Fri Jul 5 2013 Ian Wells <esmith@wellsi.com> 5.4.0-40.sme
- Remove old System Name from the Hosts DB, by Charlie Brady [SME: 7747]

* Sun Jun 23 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-39.sme
- Fix group creation when LDAP auth is enabled [SME: 7672]

* Sat Jun 8 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-38.sme
- Disable IPv6 on a default install (patch by Shad Lords) [SME: 7531]

* Sat Jun 8 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-37.sme
- Continue escaping control chars in rsyslog, just replace LF with space [SME: 7662]

* Fri Jun 7 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-36.sme
- Don't escape control characters in rsyslog [SME: 7662]

* Thu Jun 6 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-35.sme
- Use UTF-8 in the console [SME: 7591]

* Sun May 19 2013 Ian Wells <esmith@wellsi.com> 5.4.0-34.sme
- Remove redundant parts of init-accounts [SME: 3550]

* Sat May 18 2013 chris burnat <devlist@burnat.com> 5.4.0-33.sme
- Add_template_to_ssl.pem, codes by JP Pialasse [SME: 7601]

* Tue May 07 2013 Ian Wells <esmith@wellsi.com> 5.4.0-32.sme
- Require diald [SME: 7279]

* Mon May 06 2013 Ian Wells <esmith@wellsi.com> 5.4.0-31.sme
- Removal of rc.e-smith now functionality is in e-smith-service [SME: 7267]

* Sun May 05 2013 Ian Wells <esmith@wellsi.com> 5.4.0-30.sme
- Revert last change. [SME: 7227]

* Sat May 04 2013 Ian Wells <esmith@wellsi.com> 5.4.0-29.sme
- Suppress template text from /etc/inittab [SME: 7227]

* Mon Apr 22 2013 Ian Wells <esmith@wellsi.com> 5.4.0-28.sme
- Replacement of rc.e-smith by moving code into e-smith-service [SME: 7267]

* Sun Apr 21 2013 chris burnat <devlist@burnat.com> 5.4.0-27.sme
  Mon Apr 21 2013 --> Mon Apr 15 2013 or Sun Apr 21 2013 or Mon Apr 22 2013 or ....
- Fix the way '.' works in bash [SME: 7532]

* Fri Mar 22 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-26.sme
- rename /etc/ldap.conf to /etc/pam_ldap.conf (and same for .secret) [SME: 7289]

* Sat Mar 16 2013 Ian Wells <esmith@wellsi.com> 5.4.0-25.sme
- Always define InternalInterface NICBonding [SME: 7498]

* Sat Mar 16 2013 Terry Fage <trex1512@yahoo.com.au> 5.4.0-24.sme
- In the console refer to removable media instead of USB disk [SME: 7414]

* Sat Mar 16 2013 Shad L. Lords <slords@mail.com> 5.4.0-23.sme
- Fix a few more syslog => rsyslog items [SME: 7221]

* Sat Mar 16 2013 Shad L. Lords <slords@mail.com> 5.4.0-22.sme
- Remove modprobe stuff [SME: 7261]

* Sat Mar 16 2013 Shad L. Lords <slords@mail.com> 5.4.0-21.sme
- Don't be as agressive on rate limiting [SME: 7470]

* Sat Mar 16 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-20.sme
- Change syslog templates to rsyslog [SME: 7221]

* Fri Mar 15 2013 Ian Wells <esmith@wellsi.com> 5.4.0-19.sme
- Ensure existing_hwaddr is always initialized [SME: 7471]

* Thu Mar 14 2013 Ian Wells <esmith@wellsi.com> 5.4.0-18.sme
- Change System Name from mitel-networks-server to sme-server [SME: 7485]

* Sat Mar 9 2013 Shad L. Lords <slords@mail.com> 5.4.0-17.sme
- Fix user www creation in init-accounts [SME: 7319]

* Wed Mar 6 2013 Shad L. Lords <slords@mail.com> 5.4.0-16.sme
- Update package and path for pwauth [SME: 7319]
- Update init-accounts to set uid/gid correctly for pwauth

* Thu Feb 28 2013 Shad L. Lords <slords@mail.com> 5.4.0-15.sme
- Remove fragments in inittab that are no longer needed [SME: 7227]

* Mon Feb 25 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-14.sme
- Post-upgrades not fired after restore from console [SME: 7390]

* Sat Feb 23 2013 Ian Wells <esmith@wellsi.com> 5.4.0-13.sme
- Remove microcode_ctl service as now udev-driven [SME: 7397]

* Thu Feb 21 2013 Ian Wells <esmith@wellsi.com> 5.4.0-12.sme
- Increase memory limit for pppoe to 100Mb matching SME8 solution [SME: 7391]

* Thu Feb 21 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-11.sme
- Optimize user-modify-unix script and link it in bootstrap-ldap-save [SME: 7387]

* Tue Feb 19 2013 Shad L. Lords <slords@mail.com> 5.4.0-10.sme
- Add /usr/bin/passwd as a required package [SME: 7350]

* Sat Feb 9 2013 Ian Wells <esmith@wellsi.com> 5.4.0-9.sme
- Update symlink to not conflict with /etc/init.d [SME: 7322]

* Thu Feb 7 2013 Ian Wells <esmith@wellsi.com> 5.4.0-8.sme
- Add symbolic links from rsyslog to syslog to start the 
  the transition from syslog to rsyslog [SME: 7322]

* Wed Feb 6 2013 Shad L. Lords <slords@mail.com> 5.4.0-7.sme
- Remove apmd service and change package to noarch [SME: 7312]

* Sun Feb 3 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-6.sme
- Add a daemontools service to run signal-event local [SME: 7230]

* Sat Feb 2 2013 Shad L. Lords <slords@mail.com> 5.4.0-5.sme
- Obsolete nss_ldap so upgrades work [SME: 7273]

* Sat Feb 2 2013 Shad L. Lords <slords@mail.com> 5.4.0-4.sme
- Helps to spell requirements correctly

* Sat Feb 2 2013 Shad L. Lords <slords@mail.com> 5.4.0-3.sme
- Change nss_ldap to nss-pam-ldapd [SME: 7272]

* Thu Jan 31 2013 Daniel Berteaud <daniel@firewall-services.com> 5.4.0-2.sme
- Change default runlevel to 4 [SME: 7266]

* Thu Jan 31 2013 Shad L. Lords <slords@mail.com> 5.4.0-1.sme
- Roll new stream for sme9

* Tue Jan 22 2013 Ian Wells <esmith@wellsi.com> 5.2.0-67.sme
- Increase memory limit for pppoe to 100Mb [SME: 7000]

* Sun Dec 30 2012 Ian Wells <esmith@wellsi.com> 5.2.0-66.sme
- Template /etc/updatedb.conf [SME: 7090]

* Wed Jul 18 2012 Ian Wells <esmith@wellsi.com> 5.2.0-65.sme
- Make CipherSuite secure by default [SME: 7026]

* Fri Mar 16 2012 Ian Wells <esmith@wellsi.com> 5.2.0-64.sme
- Add MAC address into console network selection [SME: 6844]

* Sun Nov 6 2011 Shad L. Lords <slords@mail.com> 5.2.0-63.sme
- Initialize ExternalInterface db structure so hwaddr in console works 
  [SME: 6775]

* Mon Mar 14 2011 Daniel Berteaud <daniel@firewall-services.com> 5.2.0-62.sme
- Stop using gecos attribute in LDAP [SME: 6539]

* Mon Mar 14 2011 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-61.sme
- Fix a typo in strings [SME: 5932]

* Mon Mar 14 2011 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-60.sme
- Rework text changes in console screen in previous revision [SME: 5932]

* Mon Mar 14 2011 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-59.sme
- Only list backup targets that are writeable [SME: 5932]

* Sun Mar 13 2011 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-58.sme
- Revert admin password change through user-manager [SME: 3759]

* Sun Mar 13 2011 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-57.sme
- Allow admin password change through user-manager [SME: 3759]

* Wed Mar 2 2011 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-57.sme
- Handle no network interface scenario in console and bootstrap-console [SME: 6023]

* Mon Dec 6 2010 Daniel Berteaud <daniel@firewall-services.com> 5.2.0-56.sme
- change apache uid and gid so they become aliases for www [SME: 6425]

* Tue Nov 30 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-55.sme
- Only remove dangling symlinks in weak-updates directories [SME: 6376]

* Tue Nov 30 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-54.sme
- Fix create user gid parameter [SME: 6416]

* Mon Nov 29 2010 Daniel Berteaud <daniel@firewall-services.com> 5.2.0-53.sme
- Fix gpasswd path [SME: 6412]

* Mon Nov 22 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-52.sme
- Fix relocation of dhclient conf file [SME: 6385]

* Sun Nov 7 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-51.sme
- No longer need to pass supplemental groups to cpu [SME: 6349]

* Fri Nov 5 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-50.sme
- Allow cpu to remove empty attributes [SME: 6343]

* Thu Nov 4 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-49.sme
- Fix maxUsers patch (again) to not break setting passwords [SME: 5537]

* Thu Nov 4 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-48.sme
- Fix maxUsers patch to not break setting passwords [SME: 5537]

* Thu Nov 4 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-47.sme
- Don't put empty attributes in file for cpu [SME: 6334]

* Thu Nov 4 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-46.sme
- Add flush to tmpfile so that data is available to cpu [SME: 6334]

* Thu Nov 4 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-45.sme
- Add extra attributes to ldap objects with cpu call [SME: 6334]

* Wed Nov 3 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-44.sme
- Fix cpu critical patch missing ' [SME: 6330]

* Wed Nov 3 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-43.sme
- Make cpu calls critical only with ldap{Auth} is enabled [SME: 6330]
- Add cpu.conf and cpu-system.conf to post-upgrade event [SME: 6327]

* Tue Nov 2 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-42.sme
- Always use cpu, do unix if ldap{Auth} is disabled [SME: 6328]

* Mon Nov 1 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-41.sme
- Switch to cpu commands if ldap is master [SME: 6328]

* Mon Nov 1 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-40.sme
- Add templates for ldap authentication if enabled [SME: 6329]

* Mon Nov 1 2010 Shad L. Lords <slords@lordsfam.net> 5.2.0-39.sme
- Add cpu.conf and cpu-system.conf template/program to SME [SME: 6327]

* Thu Oct 14 2010 Daniel Berteaud <daniel@firewall-services.com> 5.2.0-38.sme
- Fix empty leases file test [SME: 6274]

* Tue Oct 12 2010 Daniel Berteaud <daniel@firewall-services.com> 5.2.0-37.sme
- Relocate dhcpd leases file [SME: 6274]

* Mon Oct 11 2010 Shad L. Lords <slords@mail.com> 5.2.0-36.sme
- Add migrate script to add missing HWaddr to interface records [SME: 6267]

* Mon Oct 11 2010 Shad L. Lords <slords@mail.com> 5.2.0-35.sme
- Make lcp options configurable [SME: 6277]

* Mon Oct 11 2010 Daniel Berteaud <daniel@firewall-services.com> 5.2.0-34.sme
- Relocate dhclient conf file [SME: 5833]

* Fri Oct 8 2010 Shad L. Lords <slords@mail.com> 5.2.0-33.sme
- Disable apmd on 64-bit arch [SME: 6170]

* Fri Oct 8 2010 Shad L. Lords <slords@mail.com> 5.2.0-32.sme
- Remove check for maxUsers [SME: 5537]

* Wed Oct 6 2010 Shad L. Lords <slords@mail.com> 5.2.0-31.sme
- Try and keep same external address for pppoe connections [SME: 6263]

* Mon Sep 27 2010 Shad L. Lords <slords@mail.com> 5.2.0-30.sme
- Add ibay groups to group membership [SME: 6247]

* Thu Sep 23 2010 Daniel Berteaud <daniel@firewall-services.com> 5.2.0-29.sme
- Prepare nss_ldap [SME: 6227]

* Sun Aug 8 2010 Ian Wells <esmith@wellsi.com> 5.2.0-28.sme
- Enable cpuspeed by default [SME: 6066]

* Sun Jul 25 2010 Charlie Brady <charlie_brady@mitel.com> 5.2.0-27.sme
- Fix syntax error in last patch. [SME: 5830]

* Mon Jul 19 2010 Charlie Brady <charlie_brady@mitel.com> 5.2.0-26.sme
- Don't exit 99 from e-smith-service script when called with 'condrestart'
  and service is disabled. [SME: 5830]

* Fri Jun 11 2010 Federico Simoncelli <federico.simoncelli@gmail.com> 5.2.0-25.sme
- FreeBusy patch fix (save account changes) [SME: 5941]

* Fri Jun 11 2010 Ian Wells <esmith@wellsi.com>  5.2.0-24.sme
- Remove checkMaxUsers patch due to regression. [SME: 5537] 

* Tue Jun  8 2010 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-23.sme
- Fix translation of local nic string in console [SME: 5571]

* Sun Jun  6 2010 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-22.sme
- Handle no network interface scenario in console [SME: 6023]

* Sat Jun 5 2010 Ian Wells <esmith@wellsi.com>  5.2.0-21.sme
- Remove checkMaxUsers(). [SME: 5537] 

* Mon May 10 2010 John H. Bennett III <bennettj@johnbennettservices.com> 5.2.0-20.sme
- Patch that will remove all FreeBusy references from e-smith-base. [SME: 5941] 

* Wed Mar  3 2010 Federico Simoncelli <federico.simoncelli@gmail.com> 5.2.0-19.sme
- Restate smartd dependency. [SME: 5814]

* Mon Mar 1 2010 Shad L. Lords <slords@mail.com> 5.2.0-18.sme
- Fix gettext errors in WAN/LAN subnet error message [SME: 5501]

* Sun Feb 14 2010 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-17.sme
- Really fix template expansion error [SME: 4528]

* Sun Feb 14 2010 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-16.sme
- Fix template expansion error [SME: 4528]

* Mon Feb 8 2010 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-15.sme
- Improve security by using SHA1 algorithm for certificate signing [SME: 5737]

* Fri Feb 5 2010 Stephen Noble <support@dungog.net> 5.2.0-14.sme
- Fix eth? swapping [SME: 4528]

* Sun Jan 31 2010 Stephen Noble <support@dungog.net> 5.2.0-13.sme
- Fix console backup from removable media [SME: 4809]

* Sat Jan 30 2010 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-12.sme
- Bump certificate encryption from 1024 bits to 2048 bits [SME: 5735]

* Thu Jan 14 2010 Filippo Carletti <filippo.carletti@gmail.com> 5.2.0-11.sme
- Fix console restore from removable media (Federico Simoncelli) [SME: 4809]

* Mon Nov 23 2009 Gavin Weight <gweight@gmail.com> 5.2.0-10.sme
- Add a dummy call so xgettext can pull translated $ifName in console configuration pages. [SME: 5571]

* Fri Nov 6 2009 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-9.sme
- Translate $ifName in console configuration pages [SME: 5571]

* Sat Oct 24 2009 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-8.sme
- Prevent IP conflicts between local and external interface in server gateway mode [SME: 5501]

* Tue Oct 20 2009 Filippo Carletti <filippo.carletti@gmail.com> 5.2.0-7.sme
- Clean up: remove unused nonetworkdrivers [SME: 5521]

* Sat Jun 6 2009 Shad L. Lords <slords@mail.com> 5.2.0-6.sme
- Clean up stray symlinks in /lib/modules before depmod [SME: 5336]

* Mon May 18 2009 Gavin Weight <gweight@gmail.com> 5.2.0-5.sme
- Allow for different mdadm output formats for DeviceSize. [SME: 5230]

* Sat Feb 14 2009 Jonathan Martens <smeserver-contribs@snetram.nl> 5.2.0-4.sme
- Auto-mount USB REV70-drive as usbdisk [SME: 5006]

* Sat Oct 25 2008 Stephen Noble <support@dungog.net> 5.2.0-3.sme
- create service link for smartd [SME: 1445]

* Mon Oct 13 2008 Shad L. Lords <slords@mail.com> 5.2.0-2.sme
- Add patch to support multiple samba roles [SME: 4172]

* Tue Oct 7 2008 Shad L. Lords <slords@mail.com> 5.2.0-1.sme
- Roll new stream to separate sme7/sme8 trees [SME: 4633]

* Tue Sep 23 2008 Stephen Noble <support@dungog.net> 4.19.0-6
- Add locale tags for email in review panel [SME: 4267]

* Sat Sep 20 2008 Shad L. Lords <slords@mail.com> 4.19.0-5
- Correct gettext type during build process [SME: 570]

* Mon Sep 15 2008 Shad L. Lords <slords@mail.com> 4.19.0-4
- Fix screen corruption in console [SME: 4155]

* Sat Sep 13 2008 Shad L. Lords <slords@mail.com> 4.19.0-3
- Fix detection of xen instance against newer kernels [SME: 4555]

* Thu Aug 28 2008 Jonathan Martens <smeserver-contribs@snetram.nl> 4.19.0-2
- Fixed warnings generated during build process [SME: 570]

* Wed Aug 20 2008 Shad L. Lords <slords@mail.com> 4.19.0-1
- Roll new dev stream.

* Sun Aug 17 2008 Gavin Weight <gweight@gmail.com> 4.18.1-22
- Add gettext to creating backup file title for localization. [SME: 4467]

* Mon Aug 11 2008 Charlie Brady <charlie_brady@mitel.com> 4.18.1-21
- Fix race condition in VPN ip-down handling which could cause loss of
  LAN connectivity. [SME: 4405]

* Sat Aug 9 2008 Shad L. Lords <slords@mail.com> 4.18.1-20
- Remove requires for whiptail.  No longer needed [SME: 4491]

* Fri Aug  8 2008 Jonathan Martens <smeserver-contribs@snetram.nl> 4.18.1-19
- Change userpassword panel to use PASSWORD_VERIFY_NEW instead of PASSWORD_NEW_VERIFY [SME: 4487]

* Thu Aug  7 2008 Jonathan Martens <smeserver-contribs@snetram.nl> 4.18.1-18
- Revert locale key PASSWORD_RESET_TITLE to RESET_PASSWORD_TITLE and move it 
  to e-smith-formmagick's general [SME: 4475]
- Reverting all *PASSWORD_NO_MATCH to *PASSWORD_VERIFY_ERROR locale keys [SME: 4476]
- Remove invalid entry tag from userpassword's locale file preventing the 
  form from displaying properly [SME: 4479]

* Tue Aug  5 2008 Jonathan Martens <smeserver-contribs@snetram.nl> 4.18.1-17
- Revert previous invalid locale changes (reverting to 4.18.1-15) [SME: 4472]

* Mon Aug  4 2008 Jonathan Martens <smeserver-contribs@snetram.nl> 4.18.1-16
- Revert some locale changes

* Tue Jul 22 2008 Gavin Weight <gweight@gmail.com> 4.18.1-15
- Add regex to support cciss device names in manageRAID.pl. [SME: 4455]

* Sat Jul 5 2008 Jonathan Martens <smeserver-contribs@snetram.nl> 4.18.1-14
- Add common <base> tags to e-smith-formmagick's general [SME: 4279]

* Sun Apr 27 2008 Jonathan Martens <smeserver-contribs@snetram.nl> 4.18.1-13
- Add common <base> tags to e-smith-formmagick's general [SME: 4279]

* Wed Apr 23 2008 Shad L. Lords <slords@mail.com> 4.18.1-12
- Fix for > 5 nics detected [SME: 4232]

* Tue Apr 22 2008 Shad L. Lords <slords@mail.com> 4.18.1-11
- Remove use of Date::Manip from ssl.crt [SME: 3155]

* Sat Apr 19 2008 Shad L. Lords <slords@mail.com> 4.18.1-10
- Fix FreeBusy param when disabled [SME: 1806]
- Remove .orig file [SME: 4228]

* Wed Apr 2 2008 Shad L. Lords <slords@mail.com> 4.18.1-9
- Remove quitConsole from menu [SME: 4154]

* Wed Apr 2 2008 Shad L. Lords <slords@mail.com> 4.18.1-8
- Really fix free/busy in usermanager [SME: 4157]

* Wed Apr 2 2008 Shad L. Lords <slords@mail.com> 4.18.1-7
- Use frames in elinks [SME: 4156]
- Set homepage for elinks [SME: 4160]

* Wed Apr 2 2008 Shad L. Lords <slords@mail.com> 4.18.1-6
- Fix free/busy field in useraccounts [SME: 4157]

* Tue Apr 1 2008 Shad L. Lords <slords@mail.com> 4.18.1-5
- Add free/busy URL entry to help kronolith contribs [SME: 1806]

* Fri Mar 28 2008 Shad L. Lords <slords@mail.com> 4.18.1-4
- Fix insert_mode for elinks on el5 platform [SME: 4127]

* Wed Mar 26 2008 Shad L. Lords <slords@mail.com> 4.18.1-3
- Set accounts to deleted before template expansion [SME: 4122]

* Wed Mar 26 2008 Shad L. Lords <slords@mail.com> 4.18.1-2
- Fix gettext strings returned by password checks [SME: 4104]

* Wed Mar 26 2008 Shad L. Lords <slords@mail.com> 4.18.1-1
- Roll new stable stream consolidating patches.

* Mon Mar 24 2008 Shad L. Lords <slords@mail.com> 4.18.0-104
- Finish removing pleasewait [SME: 126]

* Tue Mar 18 2008 Shad L. Lords <slords@mail.com> 4.18.0-103
- Add gettext to console titles. [SME: 4089]

* Sat Mar 15 2008 Stephen Noble <support@dungog.net> 4.18.0-102
- Minor translation fixes [SME: 4058] [SME: 4059]

* Wed Mar 12 2008 Shad L. Lords <slords@mail.com> 4.18.0-101
- Remove tests for removed FORM_TITLE's [SME: 4050]

* Wed Mar 12 2008 Shad L. Lords <slords@mail.com> 4.18.0-100
- Cleanup SAVE/ADD tag mixup [SME: 4045]

* Mon Mar 10 2008 Shad L. Lords <slords@mail.com> 4.18-99
  Sat Mar 10 2008 --> Sat Mar 08 2008 or Mon Mar 10 2008 or Sat Mar 15 2008 or ....
- Fix dyndns custom gettext [SME: 4032]

* Fri Mar 07 2008 Stephen Noble <support@dungog.net> 4.18-98
  Sat Mar 07 2008 --> Sat Mar 01 2008 or Fri Mar 07 2008 or Sat Mar 08 2008 or ....
- revised gettext messages [SME: 631]

* Fri Mar 07 2008 Stephen Noble <support@dungog.net> 4.18-97
  Sat Mar 07 2008 --> Sat Mar 01 2008 or Fri Mar 07 2008 or Sat Mar 08 2008 or ....
- gettext messages [SME: 631]

* Fri Mar 07 2008 Stephen Noble <support@dungog.net> 4.18-96
  Sat Mar 07 2008 --> Sat Mar 01 2008 or Fri Mar 07 2008 or Sat Mar 08 2008 or ....
- remove duplicate system password has been changed [SME: 3974]

* Fri Mar 07 2008 Stephen Noble <support@dungog.net> 4.18-95
  Sat Mar 07 2008 --> Sat Mar 01 2008 or Fri Mar 07 2008 or Sat Mar 08 2008 or ....
- EthernetAssign shouldn't be translated [SME: 3947]

* Sun Feb 17 2008 Stephen Noble <support@dungog.net> 4.18-94
- Remove pleasewait function [SME: 126]

* Sun Feb 17 2008 Stephen Noble <support@dungog.net> 4.18-93
- fix gettext formatting in three files [SME: 3938]

* Wed Feb 13 2008 chris burnat <devlist@burnat.com> 4.18-92
- Fix creation of usernames and pseudonyms with one character
- [SME: 2451]

* Wed Feb 13 2008 Stephen Noble <support@dungog.net> 4.18-91
- Remove <base> tags now in general [SME: 3911]

* Sun Feb 10 2008 Stephen Noble <support@dungog.net> 4.18-90
- Remove duplicate <base> entries [SME: 3894]

* Sat Feb 09 2008 Stephen Noble <support@dungog.net> 4.18-89
- remove unused ROUTER_DESC token from lexicon [SME: 3879]

* Sat Jan 12 2008 Shad L. Lords <slords@mail.com> 4.18-88
- remove default of 1400 MTU for interfaces [SME: 549]

* Wed Jan 09 2008 Stephen Noble <support@dungog.net> 4.18-87
- db prop to dissociate admin password from root in useraccounts.pm [SME: 3117]

* Wed Jan 09 2008 Stephen Noble <support@dungog.net> 4.18-86
- pptp connections setting mtu/mru > 1400 [SME: 549]

* Tue Jan 08 2008 Stephen Noble <support@dungog.net> 4.18-85
- console to strength validate password choice on first entry [SME: 3131]

* Tue Jan 08 2008 Stephen Noble <support@dungog.net> 4.18-84
- Auto-mount USB REV-drive as usbdisk [SME: 2972]

* Sun Jan 06 2008 Stephen Noble <support@dungog.net> 4.18-83
- ignore error returns from tar [SME: 3127]

* Sun Jan 06 2008 Stephen Noble <support@dungog.net> 4.18-82
- Use esmith::util::validatePassword on console [SME: 2173]

* Mon Dec 24 2007 Gavin Weight <gweight@gmail.com> 4.18.0-81
- Link smartd.conf to bootstrap-save-console and console-save. [SME: 1445]

* Mon Dec 24 2007 Stephen Noble <support@dungog.net> 4.18-80
- Add smartd as a disabled service with template [SME: 1445]

* Sun Dec 16 2007 Shad L. Lords <slords@mail.com> 4.18.0-79
- Lock user accounts with usermod instead of passwd [SME: 3595]

* Sun Dec 16 2007 Gavin Weight <gweight@gmail.com> 4.18.0-78
- Add symlink to fr-fr locale. [SME: 3648]

* Mon Nov 12 2007 Shad L. Lords <slords@mail.com> 4.18.0-77
- Add fix for varying partition sizes in add_raid [SME: 3547]

* Sun Nov 11 2007 Gavin Weight <gweight@gmail.com> 4.18.0-76
- Fix removal of Corporate DNS from console.  [SME: 3532]

* Fri Nov 02 2007 Gavin Weight <gweight@gmail.com> 4.18.0-75
- Remove previous change, applied to wrong package.  [SME: 3512]

* Fri Nov 02 2007 Gavin Weight <gweight@gmail.com> 4.18.0-74
- Add WPAD feature for DHCP (Thanks Hector Perez).  [SME: 3512]

* Tue Oct 16 2007 Gavin Weight <gweight@gmail.com> 4.18.0-73
- Make non-Removable pseudonyms point to admin when reassigned.  [SME: 2214]

* Sun Oct 14 2007 Gavin Weight <gweight@gmail.com> 4.18.0-72
- Adjust success text when changing admin password. [SME: 2442]

* Thu Oct 11 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-71
- Fix comparison of expected to actual SSL cert data. Also change
  truncation point for email address from 40 chars to 64. [SME: 1736].
  [Note that -70 was inadvertently skipped.]

* Tue Sep 11 2007 Gavin Weight <gweight@gmail.com> 4.18.0-69
- Move httpd logrotate.d directory to e-smith-apache. [SME: 3380]

* Tue Sep 11 2007 Gavin Weight <gweight@gmail.com> 4.18.0-68
- Rename in logrotate.d directory apache to httpd. [SME: 3380]

* Fri Sep 07 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-67
- Fix pod in groups.pm file. [SME: 3379]

* Wed Aug 22 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-66
- Relax restrictions on restore devices, to allow CDR and DVDR.
  [SME: 3126]

* Fri Aug 03 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-65
- Ensure that depmod is run for all installed kernels. [SME: 3235]

* Wed Jul 04 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-64
- Really really clear devices variable [SME: 3116]

* Sun Jul 1 2007 Shad L. Lords <slords@mail.com> 4.18.0-63
- Really clear devices variable [SME: 3116]

* Sun Jul 1 2007 Shad L. Lords <slords@mail.com> 4.18.0-62
- Clean up loop var and mount point for backup/restore [SME: 3116]

* Thu Jun 28 2007 Shad L. Lords <slords@mail.com> 4.18.0-61
- Improve usb backup error reporting [SME: 2772]

* Tue Jun 26 2007 Gavin Weight <gweight@gmail.com> 4.18.0-60
- Move the pam.d ftp/proftpd templates to e-smith-proftpd.
  [SME: 2762]

* Tue Jun 19 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-59
- Have nonetworkdrivers script exit silently if kmodule bin not found.
  [SME: 2549]

* Mon Jun 11 2007 Shad L. Lords <slords@mail.com> 4.18.0-58
- Start messagebus/haldaemon so restore works [SME: 3058]

* Sun Jun 10 2007 Stephen Noble <support@dungog.net> 4.18.0-57
- expand /etc/pam.d/login [SME: 2831]

* Wed Jun 06 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-56
- Prevent backout from console config during initial setup.
  [SME: 2540]

* Sun Jun 3 2007 Shad L. Lords <slords@mail.com> 4.18.0-55
- Clean up some more newlines [SME: 3035]
- Make raid failures more verbose [SME: 3032]
- Fix add_drive_to_raid and partition issues [SME: 2155, 2232]

* Wed May 30 2007 Gavin Weight <gweight@gmail.com> 4.18.0-54
- Update noraid text and add newline after text. [SME: 3035]

* Thu May 24 2007 Shad L. Lords <slords@mail.com> 4.18.0-53
- Don't use cracklib in system-auth [SME: 2686]

* Fri May 18 2007 Shad L. Lords <slords@mail.com> 4.18.0-52
- Use correct lib for modules

* Thu May 17 2007 Shad L. Lords <slords@mail.com> 4.18.0-51
- Updates to support xenU instance

* Wed May 9 2007 Shad L. Lords <slords@mail.com> 4.18.0-50
- Updates to support SME Server 8

* Sat May 05 2007 Gavin Weight <gweight@gmail.com> 4.18.0-49
- Fix service match RE in /sbin/e-smith/service. [SME: 2959]

* Sun Apr 29 2007 Shad L. Lords <slords@mail.com>
- Clean up spec so package can be built by koji/plague

* Sun Apr 29 2007 Shad L. Lords <slords@mail.com> 4.18.0-48
- Change to dist for tagging release
- Only include apmd for i386 platforms

* Fri Apr 27 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-47
- Validate GatewayIP address more carefully. [SME: 2928]

* Sat Apr 14 2007 Stephen Noble <support@dungog.net> 4.18.0-46
- Field to change ssh port [SME: 2382]

* Sat Apr 14 2007 Stephen Noble <support@dungog.net> 4.18.0-45
- Change fm to self in remoteaccess.pm [SME: 2382]

* Fri Apr 13 2007 Shad L. Lords <slords@mail.com> 4.18.0-44
- Make configuration dbs config(noreplace) [SME: 2527]

* Fri Apr 13 2007 Shad L. Lords <slords@mail.com> 4.18.0-43
- Adjust perm for dhcpd.conf again [SME: 2715]

* Thu Apr 12 2007 Shad L. Lords <slords@mail.com> 4.18.0-42
- Put usbback patch back in. [SME: 2483]

* Thu Apr 12 2007 Stephen Noble <support@dungog.net> 4.18.0-41
- Remove enable slocate patch [SME: 102]

* Thu Apr 12 2007 Stephen Noble <support@dungog.net> 4.18.0-40
- Change Try Again to gettext(Back) in perform backup [SME: 2483]

* Thu Apr 12 2007 Stephen Noble <support@dungog.net> 4.18.0-39
- Enable slocate in /etc/updatedb.conf [SME: 102]

* Wed Apr 11 2007 Stephen Noble <support@dungog.net> 4.18.0-38
- Make console text consistent 'Please stand by' [SME: 2493]

* Wed Apr 11 2007 Stephen Noble <support@dungog.net> 4.18.0-37
- Fix missing en-au & en-nz language noise. [SME: 2093]

* Wed Apr 11 2007 Stephen Noble <support@dungog.net> 4.18.0-36
- Fix missing list items for console [SME: 2642]

* Mon Apr 09 2007 Shad L. Lords <slords@mail.com> 4.18.0-35
- Don't attempt to add_raid_device if no raid [SME: 2484]

* Fri Apr 06 2007 Shad L. Lords <slords@mail.com> 4.18.0-34
- Add fix for perms on dhcpd.conf file [SME: 2715]

* Fri Apr 06 2007 Shad L. Lords <slords@mail.com> 4.18.0-33
- Remove fix for ftpusers.  Belongs in e-smith-proftpd. [SME: 2841]

* Fri Apr 06 2007 Shad L. Lords <slords@mail.com> 4.18.0-32
- Fix permissions on ftpusers file [SME: 2841]
- Fix permissions on pwauth file [SME: 2842]

* Thu Apr 05 2007 Shad L. Lords <slords@mail.com> 4.18.0-31
- Simplify depmod call in conf-modules [SME: 2554]

* Wed Apr 04 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-30
- Fix login pam configuration file. TODO - expand the template
  during bootstrap-console-save. [SME: 2831]

* Mon Mar 26 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-29
- Add rotate_timestamped_logfiles action, split from
  generic_template_expand. [SME: 2795]

* Thu Mar 22 2007 Shad L. Lords <slords@mail.com> 4.18.0-28
- Fix rc.e-smith to work with el4 and el5 [SME: 2510]

* Mon Mar 19 2007 Shad L. Lords <slords@mail.com> 4.18.0-27
- Add missing elements in prior pam updates [SME: 2551]

* Mon Mar 19 2007 Shad L. Lords <slords@mail.com> 4.18.0-26
- Update pam_stack to new include for el5 [SME: 2551]

* Thu Mar 08 2007 Gavin Weight <gweight@gmail.com> 4.18.0-25
- Fix missing en-gb language noise. [SME: 2633]

* Thu Mar 08 2007 Shad L. Lords <slords@mail.com> 4.18.0-24
- Call cropLeft function correctly in crt expansion [SME: 1689]

* Wed Mar 07 2007 Shad L. Lords <slords@mail.com> 4.18.0-23
- Make elinks display correctly with xterm display [SME: 444]

* Wed Mar 07 2007 Shad L. Lords <slords@mail.com> 4.18.0-22
- Add db override for crt common name [SME: 1689]

* Wed Mar 07 2007 Shad L. Lords <slords@mail.com> 4.18.0-21
- Default adding drive to raid to no [SME: 2644]

* Tue Mar 06 2007 Shad L. Lords <slords@mail.com> 4.18.0-20
- Allow nics to swap if different LAN chosen [SME: 2612]

* Tue Mar 06 2007 Shad L. Lords <slords@mail.com> 4.18.0-19
- Default WAN NIC to the *other* NIC than the one selected for LAN [SME: 2612]

* Tue Mar 06 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-18
- Combine two similar loops in selectEthernet and break overly
  long string constant. [SME: 2612]

* Tue Mar 06 2007 Shad L. Lords <slords@mail.com> 4.18.0-17
- Fix network selection dialog to include all drivers. [SME: 2612]

* Thu Mar 01 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-16
- Fix run.static file in wan service directory. [SME: 2580]

* Fri Feb 23 2007 Shad L. Lords <slords@mail.com> 4.18.0-15
- Fix glob for selecting backup devices. [SME: 2521]

* Fri Feb 23 2007 Shad L. Lords <slords@mail.com> 4.18.0-14
- User new console infobox for console backup. [SME: 2533]

* Thu Feb 22 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-13
- Use new esmith::console::infobox widget in console. [SME: 2533]

* Fri Feb 16 2007 Shad L. Lords <slords@mail.com> 4.18.0-12
- Change runsvctrl to sv to support runit v1.7.x

* Fri Feb 16 2007 Charlie Brady <charlie_brady@mitel.com> 4.18.0-11
- Restate microcode_ctl/irqbalance/cpuspeed dependencies. [SME: 2490]

* Sun Feb 11 2007 Shad L. Lords <slords@mail.com> 4.18.0-10
- Set db value for external ip before expanding templates [SME: 1977]

* Sun Feb 11 2007 Shad L. Lords <slords@mail.com> 4.18.0-9
- Do better detection of possible devices for backup/restore [SME: 2317]

* Sun Feb 11 2007 Shad L. Lords <slords@mail.com> 4.18.0-8
- Set ENV{HOME} so mysql dump works for backup [SME: 2412]

* Wed Feb 07 2007 Charlie Brady <charlieb@e-smith.com> 4.18.0-7
- Remove unused remnant dhcpcd templates. [SME: 2445]

* Wed Feb 07 2007 Charlie Brady <charlieb@e-smith.com> 4.18.0-6
- Configure elinks to obey cache control directives. I have
  no idea why that would not be the default! [SME: 2443]

* Tue Jan 30 2007 Shad L. Lords <slords@mail.com> 4.18.0-5
- Ensure gateway dev is correct for server-only [SME: 2404]

* Mon Jan 29 2007 Shad L. Lords <slords@mail.com> 4.18.0-4
- Add cancel button to backup/restore panels [SME: 2393]

* Mon Jan 29 2007 Shad L. Lords <slords@mail.com> 4.18.0-3
- Add console backup to USB [SME: 2317]

* Sun Jan 28 2007 Shad L. Lords <slords@mail.com> 4.18.0-2
- Fix backtitle for saving changes [SME: 2328]

* Fri Jan 26 2007 Shad L. Lords <slords@mail.com> 4.18.0-1
- Roll stable stream. [SME: 2328]

* Tue Jan 23 2007 Charlie Brady <charlieb@e-smith.com> 4.17.2-8
- Remove unused ifcfg-log:0 templates. [SME: 2368]

* Tue Jan 23 2007 Charlie Brady <charlieb@e-smith.com> 4.17.2-7
- Add template fragments to allow forcing of ethernet negotiation
  parameters [SME: 2362]

* Tue Jan 23 2007 Charlie Brady <charlieb@e-smith.com> 4.17.2-6
- Remove unused pam and abl templates (remnants of some stuff I
  was prototyping).

* Fri Jan 19 2007 Shad L. Lords <slords@mail.com> 4.17.2-5
- [Forward-ported from 4.17.0]
- Refactor console code considerably, and add restore from CDROM/USB
  backup capability to console.
- Remove deprecated %conf use in console. [SME: 1856]

* Fri Jan 19 2007 Shad L. Lords <slords@mail.com> 4.17.2-4
- [Ported from e-smith-base+ldap]
- Add support for use of pam_tally and/or pam_abl modules. Both
  are disabled by default.
- Update /etc/pam.d/{ftp,passwd} templates.
- Add template for /etc/pam.d/system-auth.

* Fri Jan 19 2007 Shad L. Lords <slords@mail.com> 4.17.2-3
- [Forward-ported from 4.17.0]
- Move masq fragments to e-smith-packetfilter rpm.

* Fri Jan 19 2007 Shad L. Lords <slords@mail.com> 4.17.2-2
- [Forward-ported from 4.17.0]
- Remove server-manager templates and scripts - move to e-smith-manager.
  [SME: 2023]

* Fri Jan 19 2007 Shad L. Lords <slords@mail.com> 4.17.2-1
- [Forward-ported from 4.17.0]
- Combine dhcp client, pppoe, dialup and static WAN connections into
  "wan" service. [SME 1795]

* Fri Jan 19 2007 Shad L. Lords <slords@mail.com> 4.17.2-0
- Make new development stream. Based from 4.16.0-39.

* Sun Jan 14 2007 Shad L. Lords <slords@mail.com> 4.16.0-39
- [Back-port from 4.17.0-23]
- Add admin email forwarding to modify user panel [SME: 827]

* Sat Jan 13 2007 Shad L. Lords <slords@mail.com> 4.16.0-38
- [Back-port from 4.17.0-22]
- Fix last patch so that data is pulled correctly [SME: 1034]

* Sat Jan 13 2007 Shad L. Lords <slords@mail.com> 4.16.0-37
- [Back-port from 4.17.0-21]
- Make purge-old-logs configurable via db [SME: 1034]

* Wed Jan 10 2007 Shad L. Lords <slords@mail.com> 4.16.0-36
- [Back-port from 4.17.0-20]
- Don't regenerate key and only regenerate crt when expired. [SME: 2035]

* Tue Dec 26 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-35
- [Back-port from 4.17.0-19]
- And mark admin_raidreport as only available for local mail [SME: 2139]

* Tue Dec 26 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-34
- [Back-port from 4.17.0-17, 4.17.0-18]
- Send raidmonitor output to admin_raidreport pseudonym [SME: 2139]
- And mark admin_raidreport as non-Removable [SME: 2139]

* Sat Dec 23 2006 Shad L. Lords <slords@mail.com> 4.16.0-33
- Disable raid based on /proc/partitions (which is dynamic) instead 
  of grub/device.map (which is static) [SME: 2131]

* Fri Dec 22 2006 Shad L. Lords <slords@mail.com> 4.16.0-32
- Check device size after calculating space needed. [SME: 2131]

* Fri Dec 08 2006 Shad L. Lords <slords@mail.com> 4.16.0-31
- Create partitions in order of size.  This makes sure boot is first and
  / is last.  Also last partitions fills all available space making resizing
  easier. [SME: 2131]

* Thu Dec 07 2006 Shad L. Lords <slords@mail.com>
- Update to new release naming.  No functional changes.
- Make Packager generic

* Tue Dec 05 2006 Shad L. Lords <slords@mail.com> 4.16.0-30
- Update manage raid console functions to handle all raid types [SME: 2131]

* Tue Nov 21 2006 Charlie Brady <charlie_brady@mitel.com> 4.16.0-29
- Fix warning from dhclient.conf template expansion.

* Wed Aug 30 2006 Charlie Brady <charlie_brady@mitel.com> 4.16.0-28
- Add missing LocalModule for mod_proxy_http to admin apache conf.
  [SME: 1853]

* Fri Jul 14 2006 Charlie Brady <charlie_brady@mitel.com> 4.16.0-27
- Prevent daily regeneration of SSL cert if City/Company/Department are
  empty. [SME: 1602]

* Wed Jun 28 2006 Gavin Weight <gweight@gmail.com> 4.16.0-26
- Menu text in console is incorrect for RAID5 installs. [SME: 404] 

* Wed Jun 14 2006 Gavin Weight <gweight@gmail.com> 4.16.0-25
- Modify user create page to show henry:miller not henry_miller. [SME: 531] 

* Fri Jun 9 2006 Gavin Weight <gweight@gmail.com> 4.16.0-24
- Remove lines for creating symlink to statusreport from spec file. [SME: 450] 

* Tue Jun 6 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-23
- Allow for admin account when locking null passwords, and perform
  check in post-upgrade so that the password screen will be presented
  after the reboot [SME: 1529]

* Tue Jun 6 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-22
- Correct argument ordering in last change [SME: 790, SME: 1541]

* Sun May 28 2006 Charlie Brady <charlie_brady@mitel.com> 4.16.0-21
- Increase cert serial number when new certificate is generated. [SME: 790]

* Sun May 28 2006 Charlie Brady <charlie_brady@mitel.com> 4.16.0-20
- Change ssl.crt template so that cert is regenerated if issuer information
  has changed. [SME: 1484]

* Thu Apr 27 2006 Gavin Weight <gweight@gmail.com> 4.16.0-19
- Change default shutdown value from shutdown to reboot. [SME: 1320] 

* Sun Apr 23 2006 Charlie Brady <charlie_brady@mitel.com> 4.16.0-18
- Fix syntax error introduced in last change (and reuse $rc and $choice in
  raidManage.pl). [SME: 1285,1300] 

* Fri Apr 21 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-17
- Force masq service to enabled for servergateway modes, but
  leave at current setting for serveronly. Revises -09 change [SME: 1209]

* Wed Apr 19 2006 Charlie Brady <charlie_brady@mitel.com> 4.16.0-16
- Add big warning about wiping disk to raid management screen. 
  [SME: 1285] 

* Tue Apr 18 2006 Charlie Brady <charlie_brady@mitel.com> 4.16.0-15
- Ensure that rmmod-bonding doesn't return error status if
  bonding is not enabled (e.g. during upgrade) [SME: 935]

* Tue Apr 18 2006 Charlie Brady <charlie_brady@mitel.com> 4.16.0-14
- Avoid warning from NICBondingOptions migrate fragment. [SME: 1271]

* Tue Apr 18 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-13
- Always save ssh property changes, even if sshd is disabled [SME: 1210]

* Thu Apr 13 2006 Charlie Brady <charlie_brady@mitel.com> 4.16.0-12
- Don't run kudzu at every bootup. [SME: 727]

* Tue Apr 11 2006 Charlie Brady <charlie_brady@mitel.com> 4.16.0-11
- More fixes to dhclient configuration (courtesy of Richard Schiffelers).
  [SME: 881]

* Mon Apr 10 2006 Charlie Brady <charlie_brady@mitel.com> 4.16.0-10
- Fixes to dhclient configuration (courtesy of Richard Schiffelers).
  [SME: 881]

* Thu Apr 6 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-09
- Enable the masq service to ensure that installs and upgrades
  are consistent. If someone really wants to disable it, they can 
  add a force fragment [SME: 1209]

* Thu Apr 6 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-08
- Lock accounts with bad SMB passwords [SME: 1193]

* Thu Apr 6 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-07
- Revert password length restriction changes [SME: 1193]

* Thu Apr 6 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-06
- Adjust plural in page title in last patch [SME: 1193]

* Thu Apr 6 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-05
- Adjust console logic for 14 character password restriction [SME: 1193]

* Wed Apr 5 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-04
- Only process 'network' entries in route-eth0 template [SME: 1182]

* Wed Apr 5 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-03
- Restrict passwords to 14 characters [SME: 1193]

* Tue Mar 14 2006 Gordon Rowell <gordonr@gormand.com.au> 4.16.0-02
- Rename anaconda logs, but leave a symlink. Do nothing if the log
  is already a symlink or missing [SME: 808]

* Tue Mar 14 2006 Charlie Brady <charlie_brady@mitel.com> 4.16.0-01
- Roll stable stream version. [SME: 1016]

* Tue Mar 14 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.9-20
- Ensure that each user has a Shell property in post-upgrade. 
  If they didn't have one before, set it to the current value in
  /etc/passwd. [SME: 859]

* Tue Mar 14 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.9-19
- Copy anaconda logs instead of renaming them in post-upgrade [SME: 808]
- Adjust timestamp of copied logs to logfiles2timestamp format [SME: 808]

* Mon Mar 13 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.9-18
- Change modSSL to be private in Private Server and Gateway mode [SME: 328]

* Mon Mar 13 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.9-17
- And remove now redundant calls to wherenext [SME: 986]

* Fri Mar 10 2006 Charlie Brady <charlie_brady@mitel.com> 4.15.9-16
- Fix FM page name (FirstPage => First) in a few places. [SME: 986]

* Tue Mar  7 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.9-15
- Correct typo in -13 change which hid message [SME: 964]

* Tue Mar  7 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.9-14
- Display a message for single disk installs which catches that
  case and tells people that they can add a second disk and produce
  a mirrored pair [SME: 958]

* Tue Mar  7 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.9-13
- Display a nicer message when a spare disk is available to be
  added to the pair [SME: 964]
- Blank line for consistency with other messages [SME: 964]

* Tue Mar  7 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.9-12
- Check whether a resync is in progress so we don't state that
  intervention is required when it is not [SME: 958]

* Tue Mar  7 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.9-11
- Check whether destination drive of add_mirror is already part
  of a RAID device. If so, complain and exit [SME: 870]
- Also ensure that /sbin is in the PATH

* Sun Mar  5 2006 Charlie Brady <charlie_brady@mitel.com> 4.15.9-10
- Fixes to dhclient configuration. [SME: 881]

* Fri Mar 03 2006 Mark Knox <mark_knox@mitel.com> 4.15.9-09
- Added NIC Bonding options screen in console [SME: 935]
- Migrate old NICBondingOptions to new defaults, and added new default
  options [SME: 935]
- rmmod bonding.ko in bootstrap-console-save so new options work
  without extra reboot [SME: 935]
  
* Wed Mar 01 2006 Mark Knox <mark_knox@mitel.com> 4.15.9-08
- Allow NICBondingOptions in 10bonding template fragment [SME: 918]

* Wed Mar 01 2006 Charlie Brady <charlie_brady@mitel.com> 4.15.9-07
- Bump pppoe run script mlimit from 10M to 25M. [SME: 907]

* Fri Feb 24 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.9-06
- Re-do -04 change as a patch so it sticks [SME: 863]

* Thu Feb 23 2006 Charlie Brady <charlieb@e-smith.com> 4.15.9-05
- Add templates for dhclient configuration file. [SME: 881]

* Wed Feb 22 2006 Charlie Brady <charlieb@e-smith.com> 4.15.9-04
- Remove default fragment for AdminEmail [SME: 863]

* Tue Feb 21 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.9-03
  Mon Feb 21 2006 --> Mon Feb 20 2006 or Tue Feb 21 2006 or Mon Feb 27 2006 or ....
- Change 'Reconfigure' to lower case in menu [SME: 2]

* Mon Feb 20 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.9-02
- Add requires for mdadm. We use it in the console and raid monitor
  and it won't get installed for 5.x upgrades [SME: 767]

* Fri Feb 17 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.9-01
- Roll patches to 4.15.8-60
- Trim changelog before 4.15.3-01 [SME: 828]

* Fri Feb 17 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-60
- Also rotate /var/log/anaconda.{log,syslog} in post-upgrade [SME: 808]

* Fri Feb 17 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-59
- Change 'Reconfigure' to lower case in -57 change [SME: 2]

* Fri Feb 17 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-58
- Add /root/upgrade.log and /root/upgrade.log.syslog to 
  logfiles2timestamp in post-upgrade event so we preserve 
  them across multiple upgrades [SME: 808]

* Fri Feb 17 2006 Gavin Weight <gweight@gmail.com> 4.15.8-57
- Added Reconfigure and Reboot option in console, changed
  main console menu to reflect Reconfigure option [SME: 2]

* Thu Feb 16 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-56
- Default EmailForward to 'local' in case that part of the panel
  is hidden from view [SME: 704]

* Thu Feb 16 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-55
- Adjust console title bar to 'SME Server' [SME: 726]
- Change title on "Choose administrator password" screens

* Mon Feb 13 2006 Mark Knox <mark_knox@mitel.com> 4.15.8-54
- Set EthernetDriver2 property when bonding is enabled [SME: 776]

* Mon Feb 13 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-53
- Remove cpuspeed.contrib ClearCase droppings [SME: 754]

* Sun Feb 12 2006 Charlie Brady <charlie_brady@mitel.com> 4.15.8-52
- Start bootstrap-console earlier - in particular before raidmonitor.
  Don't try to restart 'random'. [SME: 743]

* Sun Feb 12 2006 Charlie Brady <charlie_brady@mitel.com> 4.15.8-51
- Obsolete keytable service. [SME: 746]

* Sat Feb 11 2006 Shad L. Lords <slords@mail.com> 4.15.8-50
- Run kudzu -q from inittab [SME: 727]

* Thu Feb 9 2006 Charlie Brady <charlie_brady@mitel.com> 4.15.8-49
- Make bootp support optional, defaulting to 'deny'. [SME: 660]

* Thu Feb 9 2006 Gavin Weight <gweight@gmail.com> 4.15.8-48
- Removed the online-manual. [SME: 407]

* Thu Feb 9 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-47
- Hide email forwarding options on useraccounts page if there is 
  no 'smtpd' record [SME: 704]

* Wed Feb  8 2006 Charlie Brady <charlie_brady@mitel.com> 4.15.8-46
- Fix conversion of user shell from sshell to rssh. [SME: 699]

* Tue Feb 7 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-45
- Fix up location of 00openRW fragments from change 41 [SME: 659. 679]

* Mon Feb 6 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-44
- Change logic for determining RAID partitions in use [SME: 516]
- Add detailed output of the RAID state to messages log [SME: 516]

* Mon Feb 6 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-43
- Only say that a RAID device is clean if truly clean [SME: 516]
- Adjusted warning to say 'may be required' instead of 'is'

* Mon Feb 6 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-42
- Delete 'deny bootp' fragment from dhcpd.conf, reverting to
  default, which is to allow bootp. [SME: 660]

* Sun Feb  5 2006 Charlie Brady <charlie_brady@mitel.com> 4.15.8-41
- Use appropriate esmith::*DB class for 00openRW migrate fragments.
  [SME: 659]

* Tue Jan 31 2006 Gavin Weight <gweight@gmail.com> 4.15.8-40
- Added EmailForward migrate fragment [SME: 598]

* Tue Jan 31 2006 Gavin Weight <gweight@gmail.com> 4.15.8-39
- Added text periods and underscores in useraccounts [SME: 531]

* Tue Jan 31 2006 Gavin Weight <gweight@gmail.com> 4.15.8-38
- Updated copyright text in server-manager [SME: 459]

* Tue Jan 31 2006 Gavin Weight <gweight@gmail.com> 4.15.8-37
- The menu text incorrect for RAID5 configurations [SME: 404]

* Tue Jan 31 2006 Shad L. Lords <slords@mail.com> 4.15.8-36
- Disable zeroconf so 169.254.0.0/16 route isn't created [SME: 613]

* Sun Jan 29 2006 Charlie Brady <charlie_brady@mitel.com> 4.15.8-35
- Fix flip of access settings to default on first post-upgrade (e.g.
  sshd from public to private). [SME: 495]

* Sun Jan 29 2006 Charlie Brady <charlie_brady@mitel.com> 4.15.8-34
- Remove remnants of statustest. [SME: 450]

* Wed Jan 25 2006 Charlie Brady <charlie_brady@mitel.com> 4.15.8-33
- Add templated elinks config file. [SME: 444]

* Mon Jan 23 2006 Shad L. Lords <slords@mail.com> 4.15.8-32
- Help raidmonitor report more than just failures [SME: 496]

* Mon Jan 23 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-31
- Create ~/.ssh as part of skeleton home directory [SME: 456]

* Wed Jan 18 2006 Charlie Brady <charlieb@e-smith.com> 4.15.8-30
- Fix reboot problem when switching WAN from dynamic to static
  address. [SME: 500]

* Fri Jan 13 2006 Mark Knox <mark_knox@mitel.com> 4.15.8-29
- New migrate fragment to clean up NIC bonding property [SME: 449]

* Fri Jan 13 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-28
- Fix account regexp for set_password case [SME: 24]

* Wed Jan 11 2006 Mark Knox <mark_knox@mitel.com> 4.15.8-27
- New console option for ethernet bonding [SME: 449]

* Mon Jan  9 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-26
- Allow dot and underscore in account names [SME: 24]
- Default maxAcctNameLength and maxGroupNameLength to 31 [SME: 24]

* Thu Jan  5 2006 Charlie Brady <charlieb@e-smith.com> 4.15.8-25
- Avoid generating warning messages during interfaces migration
  template fragment. [SME: 354]

* Thu Jan  5 2006 Charlie Brady <charlieb@e-smith.com> 4.15.8-24
- Don't add obsolete ipsec net-pf aliases to modprobe.conf, and
  remove them if found. [SME: 390]

* Mon Jan 2 2006 Charlie Brady <charlieb@e-smith.com> 4.15.8-23
- Use regexp as well as cracklib to check admin password in console.
  [SME: 335]

* Mon Jan 2 2006 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-22
- Change heuristic for finding disks in manageRAID.pl [SME: 342]

* Sun Dec 25 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-21
  Sat Dec 25 2005 --> Sat Dec 24 2005 or Sun Dec 25 2005 or Sat Dec 31 2005 or ....
- Move testInternet console menu item to smeserver-support [SME: 364]

* Fri Dec 16 2005 Charlie Brady <charlieb@e-smith.com> 4.15.8-20
- Fix localization bug in add_mirror. [SME: 341]

* Thu Dec 15 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-19
- Remove the "In eight seconds" untruth from shutdown/reboot [SME: 86]

* Thu Dec 15 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-18
- Added modSSL{CipherSuite} default [SME: 194]

* Wed Dec 14 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-17
- Enable microcode_ctl service by default [SME: 74]

* Wed Dec 14 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-16
- Removed accounts db default for 'common'
- Added accounts db defaults for server-common and server-resources [SME: 77]

* Wed Dec 14 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-15
- Ensure that Nameservers==localhost is set for the primary domain [SME: 137]

* Wed Dec 14 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-14
- And remove db defaults for sysstat service [SME: 327]

* Wed Dec 14 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-13
- Remove sysstat startup symlink [SME: 327]

* Wed Dec 14 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-12
- Default sysconfig{PreviousSystemMode} == unknown [SME: 75]

* Wed Dec 14 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-11
- Remove Requires: sysstat [SME: 327]

* Sat Dec 10 2005 Charlie Brady <charlieb@e-smith.com> 4.15.8-10
- Move code for testing internet access into menu item file.
  [SME: 261]

* Thu Dec 8 2005 Charlie Brady <charlieb@e-smith.com> 4.15.8-09
- Fix looping in console at swap ethernet choice page. [SME: 68]

* Wed Dec 7 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-08
- Fix taint issues with RAID management menu item [SME: 253]

* Mon Dec 05 2005 Filippo Carletti <carletti@mobilia.it> 4.15.8-07
- console: DHCP range (wrong path chosen for non-English) [SME: 157]

* Fri Dec 2 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-06
- Initial cut at console menu item to (re)add RAID-1 mirror [SME: 253]
- Needs to move to /sbin/e-smith/console-menu-items, once I work out
  what I believe is a taint issue.

* Wed Nov 30 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-05
- Change 'standby' to 'stand by' in console [SME: 66]

* Wed Nov 30 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-04
- Fix routing on eth0 for multiple local networks [SME: 203]

* Wed Nov 30 2005 Gordon Rowell <gordonr@gormand.com.au> 4.15.8-03
- Bump release number only

* Mon Nov 28 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.8-02]
- Re-import head to CVS.
- Regenerate both key and cert when cert expires, not just crt. [SF: 1365965]

* Sun Nov 20 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.8-01]
- Default cpuspeed to disabled [MN00107779]

* Wed Nov 16 2005 Mark Knox <mark_knox@mitel.com>
- [4.15.7-01]
- Imported to ClearCase
- Changed console sort order from ASCII to numeric [MN00107120]

* Sun Nov 13 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.6-09]
- Add -f option to add_mirror to allow use of disks with existing
  partition tables [MN00101667]

* Sun Nov 13 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.6-08]
- Add reconfiguration reboot option to reboot panel [SF: 1349946]
- TODO: Cleanup so that the red warning header doesn't display since
  the reboot is going to happen anyway

* Mon Nov  7 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.6-07]
- Only signal-event ip-change on the BOUND action of dhclient [SF: 1344853]

* Tue Nov  1 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.6-06]
- Change DISABLED -> OFF in init script messages, and go back to standard
  alignment. [SF: 1264702, 134543]

* Mon Oct 24 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.6-05]
- Add default value of SYSFONTACM to /etc/sysconfig/i18n. [SF: 1295293]

* Mon Oct 24 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.6-04]
- Replace grub setup commands in add_mirror with an exec of an external
  script. This script will be provided by a bootloader specific package,
  e.g. e-smith-lilo or e-smith-grub. That package should include a
  "Provides: e-smith-bootloader" header, to satisfy a Requires in this
  package. [SF: 1335937]

* Thu Oct 20 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.6-03]
- Unload network drivers immediately after rc.sysinit runs, so that
  we can control the order of allocation of eth0 and eth1. [SF: 1332366]

* Mon Oct 17 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.6-02]
- Disable raid monitor if /boot/grub/device.map suggests that the system
  is a single disk system. [SF: 1269091]

* Fri Oct 14 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.6-01]
- Remove L10Ns from base packages [SF: 1309520]

* Fri Oct 14 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.5-01]
- New dev stream before relocating L10Ns

* Thu Oct 13 2005 Gordon Rowell <gordonr@gormand.com.au>
- [4.15.4-52]
- Add /sbin/e-smith/add_mirror [SF: 1325479]

* Tue Oct 11 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-51]
- Untaint menu choice when ethernet driver is chosen from menu. [SF: 1323270]

* Tue Oct 11 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-50]
- Move user-create-unix action before template expansions, so
  that getpwnam can be used in template fragments. Ditto
  for group-create-unix. [SF. 1322231]

* Sun Oct  9 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-49]
- Fix spelling mistake in useraccounts panel. [SF: 1320002]

* Fri Sep 30 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.4-48]
- Revised translation of groups panel, reordered to match
  the English lexicon - Thanks Didier Rambeau [SF: 1305184]

* Fri Sep 30 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.4-47]
- Added foot.tmpl for Italian [SF: 1309266]

* Fri Sep 30 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.4-46]
- Added Italian L10Ns - Thanks Filippo Carletti [SF: 1309266]

* Fri Sep 30 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.4-45]
- Added Italian for Please wait - we should do this through gettext
  or similar [SF: 1309288]

* Thu Sep 29 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.4-44]
- Reword Master DNS Server screen as "Corporated DNS Server", in
  line with domains panel [gordonr MN00096914]

* Mon Sep 26 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.4-43]
- German L10Ns for userpassword and console - Thanks Dietmar Berteld 
  [SF: 1293325]

* Sun Sep 25 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.4-42]
- Added German L10N - Thanks Dietmar Berteld [SF: 1293325]

* Sun Sep 25 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.4-41]
- Added "de" to pleasewait ugliness case statement and
  sorted the list alphabetically [SF: 1293325]

* Fri Sep 23 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.4-40]
- Convert [s]smtpfront-qmail to [s]smtpd in migrate fragment [SF: 1291265]

* Thu Sep 22 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-39]
- Add preliminary support for ethernet bonding on local interface.
- Modify user-modify-unix so that usermod is not called to change
  shell or GCOS field unless they need to change.

* Mon Sep 12 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-38]
- Update filelist entries for databases which have moved
  from /home/e-smith to /home/e-smith/db [SF: 1216546]

* Tue Sep  6 2005 Tony Clayton <apc@e-smith.com>
- [4.15.4-37]
- Create /mnt/floppy symlink if required in post-{install,upgrade}.
  [MN00095821]
- Haldaemon race conditions seem quite recalcitrant, so don't try to create
  /mnt/cdrom symlink. [SF: 1260322]
- Disable CTRL-C in console [tonyc SF: 1264697]
- Catch CTRL-C in console during Test Internet [tonyc SF: 1264697]

* Tue Sep  6 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-36]
- Rework user-group-modify to work around perl bug in getgrent(). [SF 1276553]

* Tue Sep  6 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-35]
- Also create /mnt/floppy symlink if required. [MN00095821]

* Mon Sep  5 2005 Gordon Rowell <gordonr@e-smith.com>
- [4.15.4-34]
- Re-add Master DNS Server console screen [gordonr MN00096910, MN00088222]

* Fri Sep  2 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-33]
- Fix race condition in /mnt/cdrom symlink creation, by creating
  symlink from haldaemon action. [SF: 1260322]

* Thu Sep  1 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-32]
- Really create /mnt/cdrom symlink if required.  [SF: 1260322]

* Tue Aug 30 2005 Shad Lords <slords@mail.com>
- [4.15.4-31]
- Update services entries to conform with RHEL4 services [SF: 1276479]

* Mon Aug 29 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-30]
- Correctly handle multiple net specification in ValidFrom for httpd-admin.
  [SF: 1273756]

* Tue Aug 23 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-29]
- Fix taint problem in license text in option 6 of the console menu.
  [SF: 1267284]

* Tue Aug 23 2005 Gordon Rowell <gordonr@gormand.com.au>
- [4.15.4-28]
- Respect Shell property of user accounts [SF: 1266706]

* Thu Aug 18 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-27]
- Modify /sbin/e-smith/service so that it runs /sbin/service unless
  runlevel is 7. [SF: 1237968]
- Only prefix /sbin/e-smith to PATH if user is root. [SF: 1250579]

* Tue Aug 16 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-26]
- Add Requires for bridge-utils and vconfig.

* Tue Aug 16 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-25]
- Add "Requires: rssh".

* Mon Aug 15 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-24]
- Update %ghost filelist entries for databases which have moved
  from /home/e-smith to /home/e-smith/db [SF: 1216546]

* Mon Aug 15 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-23]
- Create /mnt/cdrom symlink if required.  [SF: 1260322]

* Thu Aug 11 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-22]
- Add Requires: whiptail so that the out fork of whiptail from the
  newt package is installed on upgrade.

* Tue Aug  9 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-21]
- Add Requires: headers for all the additional standard daemons, to
  ensure they are installed on upgrade.

* Tue Aug  9 2005 Shad Lords <slords@mail.com>
- [4.15.4-20]
- Change httpd-admin access from local to localhost [SF: 1246986]
- Change console to use 980 instead of https to avoid warnings [SF: 1246182]
- tie console to new httpd-admin{TCPPort} property. [SF: 1246986]

* Tue Aug  2 2005 Shad Lords <slords@email.com>
- [4.15.4-19]
- Add TCPPort and access for httpd-admin [SF: 1246986]
- Fix UnsavedChanges in console [SF: 1245238]

* Thu Jul 28 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-18]
- Remove all use db_ API except in console (which will come later).

* Wed Jul 27 2005 Shad Lords <slords@mail.com>
- [4.15.4-17]
- Add systemid property to sysconfig db record. [SF: 1246367]

* Wed Jul 27 2005 Shad Lords <slords@mail.com>
- [4.15.4-16]
- Upgrade database APIs to latest standard.
- Move databases from /home/e-smith to /home/e-smith/db [SF: 1216546]

* Wed Jul 27 2005 Shad Lords <slords@mail.com>
- [4.15.4-15]
- Use https to access server-manager from console, to avoid redirect
  problems. [SF: 1246182]

* Wed Jul 27 2005 Shad Lords <slords@mail.com>
- [4.15.4-14]
- Remove hwconfig db default entry. [SF: 1246180]

* Wed Jul 27 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-13]
- Remove checking against 32 group limit from UI. Thanks to Gordon Rowell
  for the main patch. [SF: 1245421]

* Tue Jul 26 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-12]
- Patches from Shad Lords.
- Complete fix of user password validation started in 4.15.3-06.
  [SF: 1242098]
- Change default password strength to "strong". [SF: 1246178]

* Tue Jul 19 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-11]
- Patches submitted by Gordon Rowell.
- Change /etc/modules.conf templates to /etc/modprobe.conf
  and add templates.metadata/etc/modprobe.conf [SF: 1227251]
- Remove fragments 10appletalk and 95ModulePaths, since they are
  for very old migrations of /etc/modules.conf

* Tue Jul 19 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-10]
- Move quota setup in fstab template into e-smith-quota, where it
  belongs.

* Tue Jul 12 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-09]
- Add default db entries for messagebus and haldaemon. [SF: 1225899]

* Tue Jul 12 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-08]
- Add messagebus and haldaemon services, so that cdrom mount point
  etc is created as required. [SF: 1225899]

* Fri Jul  8 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-07]
- Add miscelleous performance related standard RHEL/CentOS services.

* Thu Jul  7 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-06]
- Add RAID monitoring service. [SF: 1222143]

* Tue Jul  5 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-05]
- Fix log noise from DynDNS update script. [SF: 1231871]

* Fri Jun 24 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-04]
- Change default domain name setting - I'm sure that xxx is deprecated.

* Tue Jun 21 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-03]
- Deal gracefully with missing /etc/sysconfig/keyboard file.

* Tue Jun 21 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-02]
- Remove "random" service startup symlink - no longer required, as
  prng is seeded by rc.sysinit.

* Tue Jun 21 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.4-01]
- Make new development stream - 4.15.4

* Mon Jun 20 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.3-07]
- Move httpd-admin logging from inside /var/log/httpd to /var/log/httpd-admin.
- Remove mouseconfig hack. [MN00057145]

* Fri Jun 17 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.3-06]
- Fix password strength checking of user passwords. [SF: 1222255]

* Thu Jun 16 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.3-05]
- Prefix /sbin/e-smith to $PATH, rather than append. [SF: 1222092]

* Tue Jun 14 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.3-04]
- Fix set-external-ip in case of missing ExternalIP db record. [SF: 1217877]

* Tue Jun 14 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.3-03]
- Remove smbpasswd references from chap-secrets file. Don't re-expand
  chap-secrets file during various user related events. [SF: 1215401]

* Tue Jun 14 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.3-02]
- Break up template for /etc/shells into fragments, and add
  /usr/bin/rssh. [SF: 1220145]

* Thu Jun  9 2005 Charlie Brady <charlieb@e-smith.com>
- [4.15.3-01]
- Roll new development stream - 4.15.3

