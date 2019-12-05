#!/usr/bin/perl
#===============================================================================
#
#         FILE: profile2taxlast.pl
#
#        USAGE: ./profile2taxlast.pl
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
#      CREATED: Tue May  9 17:28:45 2017 CST
#     REVISION: ---
#===============================================================================
use strict;
use warnings;
use utf8;
use Getopt::Std;

#===============================================================================
our ( $opt_i, $opt_o, $opt_h );

#===============================================================================
my $Version = "Thu Aug  3 11:14:49 CST 2017";
my $Contact = "ZHOU Yuanjie (ZHOU YJ), libranjie\@gmail.com";

#===============================================================================
#&usage if ( 0 == @ARGV );
&usage unless ( getopts('i:o:p:h') );
&usage if ( defined $opt_h );
unless ( 0 == @ARGV ) {
  &usage("with undefined options: @ARGV");
}

#===============================================================================
#&usage("lack profile table as input with: -i") unless ( defined $opt_i );
my ( $IN, $OT );
if ( defined $opt_i ) {
  open $IN, "<$opt_i" or die "read $opt_i $!\n";
}
else {
  print STDERR "lack input profile table, reading from STDIN\n";
  $IN = \*STDIN;
}
if ( defined $opt_o ) {
  $opt_o =
    ( defined $opt_i && $opt_i eq $opt_o ) ? $opt_o . ".shortlevel" : $opt_o;
  open $OT, ">$opt_o" or die "write $opt_o $!\n";
}
else {
  print STDERR "lack output profile table, reading from STDOUT\n";
  $OT = \*STDOUT;
}
&profile2taxlast( $IN, $OT );
close $IN;
close $OT;

#===============================================================================
sub profile2taxlast {
  my ( $IN, $OT ) = @_;
  my ( @head, @info, %taxlast, $i, $t );
  $_    = <$IN>;
  $_    = <$IN> if ( $_ =~ /^# Constructed from biom file/ );
  @head = split /\t/;
  print $OT $_;
  while (<$IN>) {
    chomp;
    next if (/^#/);
    @info = split /\t/;
    $info[0] = &taxlevel2short( $info[0] );
    for ( $i = 1 ; $i < @info ; ++$i ) {
      $taxlast{ $info[0] }[$i] += $info[$i];
    }
  }
  close $IN;
  foreach $i ( sort keys %taxlast ) {
    $taxlast{$i}[0] = $i;
    print $OT join "\t", @{ $taxlast{$i} };
    print $OT "\n";
  }
}

#===============================================================================
sub taxlevel2short {
  my ($tax) = @_;
  my ( @info, $last, $final );
  $tax =~ s/\s+//g;
  $tax =~ s/\[//g;
  $tax =~ s/\]//g;
  @info  = split /;/, $tax;
  $final = "";
  $last  = shift(@info);

  while ( $last =~ /[kpcofg]__\S+/ ) {
    last unless ( scalar @info );
    $final = $last;
    $last  = shift(@info);
  }
  if ( $last =~ /s__(\S+)/ ) {
    $final .= "_$1";
    $final =~ s/^g__/s__/;
  }
  elsif ( $last =~ /[kpcofg]__\S+/ ) {
    $final = $last;
  }
  elsif ( $last =~ /[kpcofgs]__$/ ) {
    $final .= ";" . $last;
  }
  elsif ( $last =~ /Other/ ) {
    $final .= ";" . $last;
  }
  elsif ( scalar @info ) {
    $final .= ";" . $last . ";" . join ";", @info;
  }
  elsif ($final) {
    $final .= ";" . $last;
  }
  else {
    $final = $last;
  }
  return $final;
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
  -i  --profile   profile table, eg genus.profile.tab, default STDIN
  -o  --profile   output last tax level of profile table, default STDOUT
  -h  --help
  \n";
  exit;
}

#===============================================================================
