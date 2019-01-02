<?php
$html = "
<html>
	<head>
		<title>Imperial EEE Exam Papers | Xav Kearney</title>
		<meta charset='utf-8' />
		<meta name='description' content='Organised collection of the Imperial Electrical & Electronic Engineering (EEE) past examination papers, from 2000-today.'>
		<link rel='shortcut icon' href='../xklogo/logo.png'>
		<meta name='author' content='Xav Kearney'>
		<link href='https://fonts.googleapis.com/css?family=Roboto' rel='stylesheet'>
	</head>
	<style>
		body {
			font-family: 'Roboto', sans-serif;
		}
		.year {
			float: left;
			margin-top: 5px;
			margin-right: 10px;
		}
</style>
	<body>
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-96943011-1', 'auto');
  ga('send', 'pageview');

</script>
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src='https://www.googletagmanager.com/gtag/js?id=UA-110453958-1'></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-110453958-1');
  gtag('config', 'UA-96943011-1');
</script>

<!--[if lt IE 8]>
<script src='details-element-polyfill.js'></script>
<![endif]-->
<!--[if IE 8]>
<script src='details-element-polyfill.js'></script>
<![endif]-->
<!--[if gt IE 8]><!-->
<script src='details-element-polyfill.js'></script>
<!--<![endif]-->";

$years = glob('*', GLOB_ONLYDIR);
foreach($years as $year) {
  $html = $html."<details class='year'><summary>$year</summary>";
  $subjects = glob($year . '/*', GLOB_ONLYDIR);
  foreach($subjects as $subject) {
	  $html = $html."<details style='text-indent: 2em;'><summary>".str_replace($year."/", "", $subject)."</summary>";
	  $papers = glob($year.'/'.substr($subject,4).'/*.pdf');
	  $html = $html."<div style='margin-left: 4em;line-height: 80%;'>";
	  foreach($papers as $paper) {
		  list($a, $b, $paper) = split('[/]', $paper);
		  $html = $html."<br><a href='$year/".substr($subject,4)."/$paper'>".str_replace(".pdf", "", $paper)."</a></br>";
	  }
	  $html = $html."<br></div></details>";
  }
  $html = $html."</details>";
}

$html = $html."
<div style='position:fixed;bottom:0px;right:10px;'><b>New shorter link: <a href='http://p.xav.ai'>p.xav.ai</a></b>. Last modified: <?php echo date('F d Y H:i:s', filemtime('index.php')); ?>. Any issues, please email 
<script language='JavaScript'>
var username = 'hi';
var hostname = 'xav.ai';
var linktext = username + '@' + hostname ;
document.write(\"<a href='\" + 'mail' + 'to:' + username + '@' + hostname + \"'>\" + linktext + \"</a>\");
</script>.</div>
<script language='JavaScript'>
function searchDetails() {
	var search_box = document.getElementById('search');
	var search_val = search_box.value.replace(' ', '-');
	console.log('Searching...');
    var items = document.getElementsByTagName('summary');
	var opened = [];
	for(var i = 0; i < items.length; i++){
		var name = items[i].innerHTML;
		if((name.toLowerCase().search(search_val.toLowerCase()) != -1) && search_val != ''){
			console.log(name);
			console.log('FOUND!');
			items[i].parentNode.setAttribute('open','');
			items[i].parentNode.parentNode.setAttribute('open','');
			opened.push(i);

		}
		else{
			items[i].parentNode.removeAttribute('open','');
			
		}
	}
	for(var j = 0; j < opened.length; j++){
		items[opened[j]].parentNode.parentNode.setAttribute('open','');
	}
		
}
</script>
<div style='position:fixed;bottom:5px;left:5px;'>
  <input type='text' id='search' onchange='searchDetails();' autofocus placeholder='Search'>
</div>
<iframe name='frame' style='display: none;'></iframe>
</body>
</html>";
$filename = "index.php";
$file = fopen($filename,"w");
$status = fwrite($file, $html);
fclose($file);
if($status == FALSE){
	echo "Updating the file failed.";
}else{
	echo "Updated file successfully.";
}
?>