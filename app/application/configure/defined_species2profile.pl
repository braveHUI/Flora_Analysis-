#!/usr/bin/perl
#===============================================================================
#
#         FILE: defined_species2profile.pl
#
#        USAGE: ./defined_species2profile.pl
#
#  DESCRIPTION:
#
#      OPTIONS: ---
# REQUIREMENTS: ---
#         BUGS: ---
#        NOTES: ---
#       AUTHOR: ZHOU Yuanjie (ZHOU YJ), libranjie@gmail.com
# ORGANIZATION: R & D Department
#      VERSION: 1.0
#      CREATED: Sat Jul 15 16:53:59 2017 CST
#     REVISION: ---
#===============================================================================
use strict;
use warnings;
use utf8;
use Getopt::Std;

#===============================================================================
our ( $opt_i, $opt_o, $opt_p, $opt_h );

#===============================================================================
my $Version = "Sat Jul 15 16:53:59 2017 CST";
my $Contact = "ZHOU Yuanjie (ZHOU YJ), libranjie\@gmail.com";

#===============================================================================
&usage if ( 0 == @ARGV );
&usage unless ( getopts('i:o:p:h') );
&usage if ( defined $opt_h );
unless ( 0 == @ARGV ) {
  &usage("with undefined options: @ARGV");
}
&usage("lack input of profile with: -i")          unless ( defined $opt_i );
&usage("lack input of species_define with: -p")   unless ( defined $opt_p );
&usage("lack result for species_define with: -o") unless ( defined $opt_o );

#===============================================================================
my ( $profile, $species_define, $result );
$profile        = $opt_i;
$species_define = $opt_p;
$result         = ( $opt_o eq $profile ) ? $opt_o . ".species_prof" : $opt_o;

#===============================================================================
my (%species);
&open_species_define( $species_define, \%species );
&defined_species2profile( $profile, \%species, $result );

#===============================================================================
sub defined_species2profile {
  my ( $profile, $species, $result ) = @_;
  my ( @info, $i, @title, %prof );
  if ( $profile =~ /\.gz/ ) {
    open IN, "gzip -dc $profile |" or die "gzip -dc $profile $!\n";
  }
  else {
    open IN, "<$profile" or die "read $profile $!\n";
  }
  open OT, ">$result" or die "write $result $!\n";
  chomp( $_ = <IN> );
  chomp( $_ = <IN> ) if ( $_ =~ /^# Constructed from biom file/ );
  s/^#//g;
  print OT $_, "\n";
  @title = split /\t/;
  while (<IN>) {
    chomp;
    @info = split /\t/;
    next unless ( defined $$species{ $info[0] } );
    for ( $i = 1 ; $i < @info ; ++$i ) {
      next
        unless (
        $info[$i] =~ /^([+-]?)(?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?$/ );
      $prof{ $$species{ $info[0] } }[$i] += $info[$i];
    }
  }
  close IN;
  foreach $i ( sort keys %prof ) {
    $prof{$i}[0] = $i;
    print OT join "\t", @{ $prof{$i} };
    print OT "\n";
  }
  close OT;
}

#===============================================================================
sub open_species_define {
  my ( $species_define, $species ) = @_;
  my (@info);
  open SP, "<$species_define" or die "read $species_define $!\n";
  while (<SP>) {
    chomp;
    next if (/^#/);
    @info = split /\t/;
    $species->{ $info[0] } = ( defined $info[1] ) ? $info[1] : $info[0];
  }
  close SP;
}

#===============================================================================
sub usage {
  my ($reason) = @_;
  print STDERR "
  ==============================================================================
  $reason
  ==============================================================================
  " if ( defined $reason );
  print STDERR "
  Last modify: $Version
  Contact: $Contact

  Usage:
  \$perl $0 [options]
  -i  --input profile table, required
  -p  --species_define file, required
  -o  --result for species_define.prof, required
  -h  --help
  \n";
  exit;
}
