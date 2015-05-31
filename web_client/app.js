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
			e.find(".content").text(data.posts[p].content)
			e.find(".like-panel .likes").text(data.posts[p].like)
			e.find(".like-panel .dislikes").text(data.posts[p].dislike)
		}
	});
});
