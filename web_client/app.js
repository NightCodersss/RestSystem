var RestSystemServer = "http://localhost:12888"

$(document).ready(function(){
	$.ajax({
		url: RestSystemServer,
		method: "POST",
		data: JSON.stringify({action: "get_posts"}),
	}).done(function(res) {
		console.log(res)
		data = JSON.parse(res)
		for(var p in data.posts)
		{
			e = $("<div class='post'><div class='content'></div><div class='like-panel'><div class='likes'></div><div class='dislikes'></div></div></div>")
			$(".posts").append(e)
			e.find(".post .content").text(p.content)
			e.find(".post .like-panel .likes").text(p.like)
			e.find(".post .like-panel .dislikes").text(p.dislike)
		}
	});
});
