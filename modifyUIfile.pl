#!/usr/bin/perl

# Add the lasagna import to the end of the UI file and modify the plotwidget object creation to 
# inherit from it.
#
# TODO: make my own widget so I don't have to use this stupid hack

use strict ; 
use warnings;

my $fName = 'lasagna_mainWindow.py' ;


# open the file
open (UI_FILE, "+<$fName") or die "$! error opening fname" ;

my $ui_file ; 
{
	local $/ = undef;
	$ui_file = (<UI_FILE>);
}

#Add replace the PlotWidget lines to go from:
# PlotWidget(self.centralwidget)
# to:
# PlotWidget(self.centralwidget,viewBox=lasagna_viewBox())

$ui_file =~ s{PlotWidget\(self\.centralwidget\)}{PlotWidget(self.centralwidget,viewBox=lasagna_viewBox())}g ;

#add the import for the lasagna_viewBox
my $importString = 'from lasagna_viewBox import lasagna_viewBox';

$ui_file = $ui_file . $importString . "\n" ;


# Overwrite the UI file
seek (UI_FILE, 0, 0)                     or die "Can't seek to start of $fName."     ;
print UI_FILE $ui_file                   or die "Can't write Sue's dates to $fName." ;
truncate(UI_FILE, tell(UI_FILE))         or die "Can't truncate $fName."             ;
close UI_FILE 						     or die "Can't close file"                   ;
