#!/usr/bin/perl
#===============================================================================
#
#         FILE: profile2equalize.pl
#
#        USAGE: ./profile2equalize.pl
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
#      CREATED: Fri Jul 14 22:09:56 2017 CST
#     REVISION: ---
#===============================================================================
use strict;
use warnings;
use utf8;
use Getopt::Std;

#===============================================================================
our ( $opt_i, $opt_o, $opt_h );

#===============================================================================
my $Version = "Fri Jul 14 22:09:56 2017 CST";
my $Contact = "ZHOU Yuanjie (ZHOU YJ), libranjie\@gmail.com";

#===============================================================================
&usage if ( 0 == @ARGV );
&usage unless ( getopts('i:o:h') );
&usage if ( defined $opt_h );
unless ( 0 == @ARGV ) {
  &usage("with undefined options: @ARGV");
}

#===============================================================================
my ( $profile, $result );
$profile = ( defined $opt_i ) ? $opt_i : 0;
$result  = ( defined $opt_o ) ? $opt_o : 0;

#===============================================================================
my ( $IN, $OT );
if ($profile) {
  if ( $profile =~ /\.gz/ ) {
    open $IN, "gzip -dc $profile |" or die "gzip -dc $profile $!\n";
  }
  else {
    open $IN, "<$profile" or die "read $profile $!\n";
  }
}
else {
  print STDERR "lack input profile table, reading from STDIN\n";
  $IN = \*STDIN;
}
if ($result) {
  $result = ( $result eq $profile ) ? $result . ".prof" : $result;
  open $OT, ">$result" or die "write $result $!\n";
}
else {
  print STDERR "lack output profile table, reading from STDOUT\n";
  $OT = \*STDOUT;
}
&profile2equalize( $IN, $OT );

#===============================================================================
sub profile2equalize {
  my ( $IN, $OT ) = @_;
  my ( @title, @info, $i, %total );
  chomp( $_ = <$IN> );
  chomp( $_ = <$IN> ) if ( $_ =~ /^# Constructed from biom file/ );
  @title = split /\t/;
  while (<$IN>) {
    chomp;
    @info = split /\t/;
    for ( $i = 1 ; $i < @info ; ++$i ) {
      next
        unless (
        $info[$i] =~ /^([+-]?)(?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?$/ );
      $total{ $title[$i] } += $info[$i];
    }
  }
  seek $IN, 0, 0;
  chomp( $_ = <$IN> );
  chomp( $_ = <$IN> ) if ( $_ =~ /^# Constructed from biom file/ );
  print $OT $_, "\n";
  while (<$IN>) {
    chomp;
    @info = split /\t/;
    print $OT $info[0];
    for ( $i = 1 ; $i < @info ; ++$i ) {
      if ( $info[$i] =~ /^([+-]?)(?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?$/ ) {
        print $OT "\t", $info[$i] / $total{ $title[$i] };
      }
      else {
        print $OT "\t$info[$i]";
      }
    }
    print $OT "\n";
  }
}

#===============================================================================
sub usage {
  my ($reason) = @_;
  print STDERR "
  ================================================================================
  $reason
  ================================================================================
  " if ( defined $reason );
  print STDERR "
  Last modify: $Version
  Contact: $Contact

  Usage:
  \$perl $0 [options]
  -i  --profile   profile table, eg profile.table, default STDIN
  -o  --profile   output relative abundance profile table, default STDOUT
  -h  --help
  \n";
  exit;
}
