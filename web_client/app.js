var RestSystemServer = "http://localhost:12888"
var Token;

function onSignIn(googleUser)
{
	var profile = googleUser.getBasicProfile();
	console.log("ID: " + profile.getId()); // Don't send this directly to your server!
	console.log("Name: " + profile.getName());
	console.log("Image URL: " + profile.getImageUrl());
	console.log("Email: " + profile.getEmail());

	// The ID token you need to pass to your backend:
	var id_token = googleUser.getAuthResponse().id_token;
	console.log("ID Token: " + id_token);
	Token = id_token;
	$.ajax({
		url: RestSystemServer,
		method: "POST",
		data: JSON.stringify({action: "signin", token: Token}),
	}).done(function(res) {
		console.log(res)
		data = JSON.parse(res)
		if(data.instructions == "register")
		{
			$(".signin").hide()
			$(".registration").show()
		}
		else
		{
			$(".signin").hide()
			$(".app_window").show()
		}
	})
}

$(document).ready(function(){
	$(".app_window").hide()
	$(".registration").hide()
	$(".registration .create").click(function(){
		$.ajax({
			url: RestSystemServer,
			method: "POST",
			data: JSON.stringify({action: "create_user", token: Token, name: $(".registration .user_name").val(), group_name: $(".registration .group_name").val()}),
		}).done(function(res) {
			console.log(res)
			data = JSON.parse(res)
			$(".registration").hide()
			$(".app_window").show()
		})
	})
	$(".registration .join").click(function(){
		$.ajax({
			url: RestSystemServer,
			method: "POST",
			data: JSON.stringify({action: "create_user", token: Token, name: $(".registration .user_name").val(), gid: $(".registration .gid").val()}),
		}).done(function(res) {
			console.log(res)
			data = JSON.parse(res)
			$(".registration").hide()
			$(".app_window").show()
		})
	})
	return
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
