#!/usr/local/cpanel/3rdparty/bin/perl
# cpanel - t/SOURCES-fcgid.conf                   Copyright(c) 2016 cPanel, Inc.
#                                                           All rights Reserved.
# copyright@cpanel.net                                         http://cpanel.net
# This code is subject to the cPanel license. Unauthorized copying is prohibited

use strict;
use warnings;
use base qw( Test::Class );

use Test::More;
use Test::NoWarnings;
use Test::File;
use File::Slurp;
use FindBin;

sub fail_if_returned_early { return 1 }

sub init : Test( startup => 1 ) {
    my ($self) = @_;

    $self->{spec}->{path}           = ( glob("$FindBin::Bin/../SPECS/*.spec") )[0];
    $self->{conf}->{apache}->{path} = "$FindBin::Bin/../SOURCES/fcgid.conf";
    $self->{conf}->{module}->{path} = "$FindBin::Bin/../SOURCES/500-mod_fcgid.conf";

    ok( defined $self->{spec}->{path} && -s $self->{spec}->{path}, "Spec file exists and contains information" );
    $self->{spec}->{content} = File::Slurp::read_file( $self->{spec}->{path} );

    return 1;
}

sub test_validate_spec : Test {
    my ($self) = @_;

    note "Validating spec file";

    like( $self->{spec}->{content}, qr/^\%define\s+release_prefix\s+\d+\s*$/m, "Contains the required release_prefix for OBS" );

    return 1;
}

sub test_validate_apache_conf : Tests(4) {
    my ($self) = @_;

    note "Validating default mod_fcgid Apache configuration";

    my $path = $self->{conf}->{apache}->{path};
    ok( defined $path && -s $path, "Default configuration exists in SOURCES directory" );
    like( $self->{spec}->{content}, qr{\%config\(noreplace\).+?/fcgid\.conf\s*$}m, "SPEC file appears to install an Apache configuration that the user can modify" );
    my $content = File::Slurp::read_file($path);
    like( $content, qr/^\s*FcgidMaxRequestLen\s+\d+\s*$/m,    "Apache configuration specifies a default FcgidMaxRequestLen value" );
    like( $content, qr/^\s*MaxRequestsPerProcess\s+\d+\s*$/m, "Apache configuration specifies a default MaxRequestsPerProcess value" );

    return 1;
}

sub test_validate_module_conf : Tests(3) {
    my ($self) = @_;

    note "Validating mod_fcgid loading into Apache";

    my $path = $self->{conf}->{module}->{path};
    ok( defined $path && -s $path, "Module loading configuration exists in SOURCES directory" );
    like( $self->{spec}->{content}, qr{^\%config\s+.+?/500\-mod_fcgid\.conf}m, "Appears to install a LoadModule configuration file the user cannot modify" );
    my $content = File::Slurp::read_file($path);
    like( $content, qr{^\s*LoadModule\s+fcgid_module\s+modules/mod_fcgid\.so}m, "Config contains the correct syntax so it can be loaded by Apache" );

    return 1;
}

sub test_validate_rundir : Tests(5) {
    my ($self) = @_;

    note "Validating the integrity of the mod_fcgid run directory";

    my @matches = $self->{spec}->{content} =~ m{^\%(attr\(\d+,\w+,\w+\))\s*\%\{_rundir\}/mod_fcgid\s*$}gm;
    is( scalar @matches, 1, "Found the /run/mod_fcgid directory" );
    like( $matches[0], qr/attr\(0750,nobody,root\)/, "The /run/mod_fcgid directory contains correct permissions" );

    @matches = $self->{spec}->{content} =~ m{^Source\d*:\s*mod_fcgid\-tmpfs\.conf}igm;
    is( scalar @matches, 1, 'Found the tmpfiles.d configuration file for /run/mod_fcgid in spec file' );

    my $src = "$FindBin::Bin/../SOURCES/mod_fcgid-tmpfs.conf";
    ok( -s $src, 'Found tmpfiles.d configuration file in the SOURCES directory' );
    file_contains_like( $src, qr{^\s*d\s+(?:/var)?/run/mod_fcgid\s+0750\s+nobody\s+root\s*}, 'The /run/mod_fcgid config for tmpfiles.d is correct' );

    return 1;
}

if ( !caller ) {
    my $t = __PACKAGE__->new();
    plan tests => $t->expected_tests(+1);
    $t->runtests();
}
