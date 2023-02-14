#!/usr/bin/env perl
# this script prints a pretty report from rsnapshot output
# in the rsnapshot.conf you must set
# verbose >= 4
# and add --stats to rsync_long_args
# then setup crontab 'rsnapshot daily 2>&1 | rsnapreport.pl | mail -s"SUBJECT" backupadm@adm.com
# don't forget the 2>&1 or your errors will be lost to stderr
################################
## Copyright 2006 William Bear
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
################################
use strict;
use warnings;
use English '-no_match_vars';

my $bufsz = 2;
my %bkdata=();

# --- modification start ---
my @errors=();
my @warnings=();
# --- modification end ---

# --- modification start ---
sub min {
    my $min = shift;
    foreach (@_) {
        $min = $_ if $_ < $min;
    }
    return $min;
}

sub max {
    my $max = shift;
    foreach (@_) {
        $max = $_ if $_ > $max;
    }
    return $max;
}
# --- modification end ---



sub pretty_print(){
	my $ofh = select(STDOUT);
	$FORMAT_NAME="BREPORTBODY";
	$FORMAT_TOP_NAME="BREPORTHEAD";
	select($ofh);


	# --- modification start ---

	# this modification fixes a problem that backup source location possible
	# being truntcated.

	# calculate the column length for each row

	my $col_source_len = 8;
	my $col_files_len = 13;
	my $col_filest_len = 13;
	my $col_bytes_len = 10;
	my $col_bytest_len = 10;
	my $col_filelistgentime_len = 15;
	my $col_filelistxfertime_len = 16;

	foreach my $source (sort keys %bkdata){
	
		if($bkdata{$source} =~ /error/i) { print "ERROR $source $bkdata{$source}"; next; }
		
		my $files = $bkdata{$source}{'files'};
		my $filest = $bkdata{$source}{'files_tran'};
		my $bytes = $bkdata{$source}{'file_size'}/1000000; # convert to MB
		my $bytest = $bkdata{$source}{'file_tran_size'}/1000000; # convert to MB
		my $filelistgentime = $bkdata{$source}{'file_list_gen_time'}; # ends with "seconds"
		my $filelistxfertime = $bkdata{$source}{'file_list_trans_time'}; # ends with "seconds"
		
		# convert each to string...
		$source =~ s/^[^\@]+\@//; # remove username (in case using ssh)
		$files = sprintf("%u", $files);
		$filest = sprintf("%u", $filest);
		$bytes = sprintf("%.2f", $bytes);
		$bytest = sprintf("%.2f", $bytest);
		#$filelistgentime = sprintf("%s", $filelistgentime);
		#$filelistxfertime = sprintf("%s", $filelistxfertime);
		
		# leave at least two (2) spaces for padding
		$col_source_len = max($col_source_len, 2 + length($source));
		$col_files_len = max($col_files_len, 2 + length($files));
		$col_filest_len = max($col_filest_len, 2 + length($filest));
		$col_bytes_len = max($col_bytes_len, 2 + length($bytes));
		$col_bytest_len = max($col_bytest_len, 2 + length($bytest));
		$col_filelistgentime_len = max($col_filelistgentime_len, 2 + length($filelistgentime));
		$col_filelistxfertime_len = max($col_filelistxfertime_len, 2 + length($filelistxfertime));
	}
	
	
	
	
	# print header row
	printf "%-${col_source_len}s%-${col_files_len}s%-${col_filest_len}s%-${col_bytes_len}s%-${col_bytest_len}s%-${col_filelistgentime_len}s%-${col_filelistxfertime_len}s\n","SOURCE","TOTAL FILES", "FILE TRANS", "TOTAL MB", "MB TRANS", "LIST GEN TIME", "FILE XFER TIME";




	# print seperator line
	print "-" x $col_source_len;
	print "-" x $col_files_len;
	print "-" x $col_filest_len;
	print "-" x $col_bytes_len;
	print "-" x $col_bytest_len;
	print "-" x $col_filelistgentime_len;
	print "-" x $col_filelistxfertime_len;
	print "\n";
	



	# finally, print each all backup stats
	foreach my $source (sort keys %bkdata){
		
		if($bkdata{$source} =~ /error/i) { print "ERROR $source $bkdata{$source}"; next; }
		
		my $files = $bkdata{$source}{'files'};
		my $filest = $bkdata{$source}{'files_tran'};
		my $bytes = $bkdata{$source}{'file_size'}/1000000; # convert to MB
		my $bytest = $bkdata{$source}{'file_tran_size'}/1000000; # convert to MB
		my $filelistgentime = $bkdata{$source}{'file_list_gen_time'};
		my $filelistxfertime = $bkdata{$source}{'file_list_trans_time'};
		
		# convert each to string...
		$source =~ s/^[^\@]+\@//; # remove username (in case using ssh)
		$files = sprintf("%u", $files);
		$filest = sprintf("%u", $filest);
		$bytes = sprintf("%.2f", $bytes);
		$bytest = sprintf("%.2f", $bytest);
		#$filelistgentime = sprintf("%s", $filelistgentime);
		#$filelistxfertime = sprintf("%s", $filelistxfertime);
		
		printf "%-${col_source_len}s%-${col_files_len}s%-${col_filest_len}s%-${col_bytes_len}s%-${col_bytest_len}s%-${col_filelistgentime_len}s%-${col_filelistxfertime_len}s\n", $source, $files, $filest, $bytes, $bytest, $filelistgentime, $filelistxfertime;

		
	}

	# --- modification end ---

}

sub nextLine($){
	my($lines) = @_;
	my $line = <>;
	push(@$lines,$line);
	return shift @$lines;
}


my @rsnapout = ();

# load readahead buffer
for(my $i=0; $i < $bufsz; $i++){
	$rsnapout[$i] = <>;
}

while (my $line = nextLine(\@rsnapout)){
	if($line =~ /^[\/\w]+\/rsync/) { # find start rsync command line
		my @rsynccmd=();
		while($line =~ /\s+\\$/){ # combine wrapped lines
			$line =~ s/\\$//g;
			$line .= nextLine(\@rsnapout);
		}
		
		# --- modification start ---

		# replace spaces inside the backup source location
		$line =~ s/\\ /_/g;
		
		# --- modification end -
		
		
		push(@rsynccmd,split(/\s+/,$line)); # split into command components
		my $source = $rsynccmd[-2]; # count backwards: source always second to last
		#print $source;
		while($line = nextLine(\@rsnapout)){
  			# this means we are missing stats info
			if($line =~ /^[\/\w]+\/rsync/){
				unshift(@rsnapout,$line);
				push(@errors,"$source NO STATS DATA");
				last;
			}
			# stat record
			if($line =~ /^total size is\s+\d+/){ last; } # this ends the rsync stats record
			# Number of files: 1,325 (reg: 387, dir: 139, link: 799)
			elsif($line =~ /Number of files:\s+([\d,]+)/){
				$bkdata{$source}{'files'}=$1;
				$bkdata{$source}{'files'}=~ s/,//g;
			}
			# Number of regular files transferred: 1
			elsif($line =~ /Number of (regular )?files transferred:\s+([\d,]+)/){
				$bkdata{$source}{'files_tran'}=$2;
			}
			# Total file size: 1,865,857 bytes
			elsif($line =~ /Total file size:\s+([\d,]+)/){
				$bkdata{$source}{'file_size'}=$1;
				$bkdata{$source}{'file_size'}=~ s/,//g;
			}
			elsif($line =~ /Total transferred file size:\s+([\d,]+)/){
				$bkdata{$source}{'file_tran_size'}=$1;
				$bkdata{$source}{'file_tran_size'}=~ s/,//g;
			}
			elsif($line =~ /File list generation time:\s+(.+)/){
				$bkdata{$source}{'file_list_gen_time'}=$1;
			}
			elsif($line =~ /File list transfer time:\s+(.+)/){
				$bkdata{$source}{'file_list_trans_time'}=$1;
			}
			
			# --- modification start ---
	
			# we encountered rsync error(s)
			elsif($line =~ /^(rsync error|ERROR): /){
				$line =~ s/^(ERROR): //g;
				$line =~ s/^\s+|\s+$//g; #<< remove both leading and trailing whitespace(s)
				push(@errors,"$source $line");
			} 
			
			# --- modification end ---
		}
	}
	
	# --- modification start ---
	
	# we encountered warning(s)
	elsif($line =~ /^(rsync error|WARNING): /){
		$line =~ s/^(WARNING): //g;
		$line =~ s/^\s+|\s+$//g; #<< remove both leading and trailing whitespace(s)
		push(@warnings,$line);
	} 
	
	# we encountered error(s)
	elsif($line =~ /^(ERROR): /){
		$line =~ s/^(ERROR): //g;
		$line =~ s/^\s+|\s+$//g; #<< remove both leading and trailing whitespace(s)
		push(@errors,$line);
	}
	
	# --- modification end ---
	
}





# --- modification start ---

# backup summary
print "\n";
pretty_print();


# warning messages, if any
printf "\n%i WARNING(S)\n\n", scalar @warnings ;
if(scalar @warnings > 0){
	print join("\n",@warnings);
}
print "\n";


# error messages, if any
printf "\n%i ERROR(S)\n\n", scalar @errors ;
if(scalar @errors > 0){
	print join("\n",@errors);
}
print "\n";


# get the full path to a Perl script that is executing?
use File::Basename;
my $this_script_dir = dirname(__FILE__);


# tell what version does ycspomeep be currently using.
my $ycspomeep_version = `cd $this_script_dir && /usr/bin/python3 -c "from constants import CURRENT_VERSION; print(CURRENT_VERSION);"`;

$ycspomeep_version =~ s/\n//g; # << remove newline
$ycspomeep_version =~ s/\r//g; # << remove newline also

printf "*** This mail was sent by ycspomeep version %s. ***\n\n", "$ycspomeep_version";

# --- modification end ---
