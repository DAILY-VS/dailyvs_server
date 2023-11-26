document.addEventListener("DOMContentLoaded", () => {
  const likeButton = document.getElementById("like-button");
  const pollId = likeButton.getAttribute("data-poll-id");
  const heartImage = likeButton.querySelector("img");
  var isAuthenticated = "{{ user.is_authenticated }}";

  axios
    .get(`/get-like-status/${pollId}/`)
    .then((response) => {
      const userLikesPoll = response.data.user_likes_poll;

      if (userLikesPoll) {
        heartImage.src = "../../../static/img/icon/pink_heart.png";
      } else {
        heartImage.src = "../../../static/img/icon/blank_heart.png";
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });

  likeButton.addEventListener("click", () => {

    console.log("클릭!");

    axios
      .post(
        "/like/",
        { poll_id: pollId },
        {
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
          },
        }
      )
      .then((response) => {
      
          const message = response.data.message;
          const likeCount = response.data.like_count;
          let userLikesPoll = response.data.user_likes_poll;

        if (message === "좋아요 취소") {
          heartImage.src = "../../../static/img/icon/blank_heart.png";
          userLikesPoll = false;
          localStorage.setItem("userLikesPoll", false);
        } else {
          heartImage.src = "../../../static/img/icon/pink_heart.png";
          userLikesPoll = true;
          localStorage.setItem("userLikesPoll", true);
        }

        document.querySelector("#like-count").textContent = likeCount;
        likeButton.setAttribute("data-user-likes", userLikesPoll);
      
      })
      .catch((error) => {
        if (error.response && error.response.status === 401) {
          // 로그인이 필요한 경우
          if (confirm("로그인이 필요합니다. 로그인 페이지로 이동하시겠습니까?")) {
            var loginUrl = "/account/login/";
            window.location.href = loginUrl;
          }
        } else {
          console.error("Error:", error);
        }
      });
  });

  const userLikesPoll = localStorage.getItem("userLikesPoll");
  if (userLikesPoll === "true") {
    heartImage.src = "../../../static/img/icon/pink_heart.png";
  } else {
    heartImage.src = "../../../static/img/icon/blank_heart.png";
  }

  function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
  }
});
