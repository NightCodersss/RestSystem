var RestSystemServer = "localhost:12888"

$(document).ready(function(){
	$.ajax({
		url: RestSystemServer,
		method: "POST",
		data: {action: "get_posts"}
	}).done(function(res) {
		  console.log(res)
	});
});
