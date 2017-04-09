#!/usr/bin/perl -w
#Written by Costa Paraskevopoulos in April 2017
#Web scraper for restaurant data on zomato.com

use File::Path qw(rmtree);

#caches all the downloaded zomato pages
for $i (1..10) {
	if (! -e "zomato$i.html") {
		last;
	}
	open ZOMATO, '<', "zomato$i.html";
	push @lines, <ZOMATO>;
}

$i = -1;
$skip = 1;

#finds all restaurant entries on the page
for $line (@lines) {
	if ($line =~ /<\s*div\s+class\s*=\s*"card\s+search-snippet-card\s+search-card\s*">/) {
		$i++;
		$skip = 0;
	} elsif ($skip == 0) {
		$results[$i] .= $line;
	}
}

rmtree 'restaurants';
mkdir 'restaurants' or die "Cannot create 'restaurants': $!\n";
$i = 0;

#extracts data from each entry and outputs to individual files
for $result (@results) {
	my ($name, $phone) = $result =~ /<a class="item res-snippet-ph-info" data-res-name ="(.*)" data-phone-no-str = "(.*)">/;
	my ($hours) = $result =~ /<div class="res-timing clearfix" title="([^"]*)">/;
	my ($cost) = $result =~ /Cost for two:<\/span><span class="col-s-11 col-m-12 pl0" >A\$(.*)<\/span><\/div>/;
	my ($address) = $result =~ /<div style=" max-width:370px; " class="col-m-16 search-result-address grey-text nowrap ln22" title="(.*)">/;
	my ($cuisine) = $result =~ /<div class='clearfix'><span class='col-s-5 col-m-4 ttupper fontsize5 grey-text' >Cuisines: <\/span><span class='col-s-11 col-m-12 nowrap  pl0' ><a title="([^"]*)" href/;

	#discards bad data
	if (!defined $name || !defined $phone || !defined $hours || !defined $cost || !defined $address || !defined $cuisine) {
		continue;
	}

	open FILE, '>', "restaurants/$i";
	$cost = int($cost / 2); #maps "cost for two" to "cost per meal"
	print FILE "$name\n$address\n$phone\n$hours\n$cuisine\n$cost\n";
	close FILE;
	$i++;
}
