const openReply = (commentId) => {
  //var commentId = btn.getAttribute("data-comment-id");
  var parentContainer = document.querySelector(
    ".nested-reply-container[data-parent-id='" + commentId + "']"
  );
  var nestedInputContainer = document.querySelector(
    ".nested-reply-input-container[data-parent-id='" + commentId + "']"
  );

  if (parentContainer) {
    if (
      parentContainer.style.display === "none" ||
      parentContainer.style.display === ""
    ) {
      parentContainer.style.display = "block";
      if (nestedInputContainer) {
        nestedInputContainer.style.display = "block";
      }
    } else {
      parentContainer.style.display = "none";
      if (nestedInputContainer) {
        nestedInputContainer.style.display = "none";
      }
    }
  }
}

//대댓글 토글
document.addEventListener("DOMContentLoaded", function () {
  var toggleButtons = document.querySelectorAll(".reply-toggle-btn");

  toggleButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      var commentId = this.getAttribute("data-comment-id");
      var parentContainer = document.querySelector(
        ".nested-reply-container[data-parent-id='" + commentId + "']"
      );
      var nestedInputContainer = document.querySelector(
        ".nested-reply-input-container[data-parent-id='" + commentId + "']"
      );

      if (parentContainer) {
        if (
          parentContainer.style.display === "none" ||
          parentContainer.style.display === ""
        ) {
          parentContainer.style.display = "block";
          if (nestedInputContainer) {
            nestedInputContainer.style.display = "block";
          }
        } else {
          parentContainer.style.display = "none";
          if (nestedInputContainer) {
            nestedInputContainer.style.display = "none";
          }
        }
      }
    });
    
    // 대댓글 수 초기화
    var commentId = button.getAttribute("data-comment-id");
    updateNestedCount(commentId);
  });

  // 페이지 로드 시 모든 댓글의 대댓글 수 초기화
  var allCommentButtons = document.querySelectorAll(".reply-toggle-btn");
  allCommentButtons.forEach(function (button) {
    var commentId = button.getAttribute("data-comment-id");
    updateNestedCount(commentId);
  });
});



//대댓글 수 카운트
function updateNestedCount(comment_id) {
  var url = "/calculate-nested-count/" + comment_id + "/";
  $.ajax({
    type: "GET",
    url: url, // 서버에서 대댓글 수를 계산하는 뷰의 URL
    dataType: "json",
    success: function (response) {
      var nestedCountSpan = $("#nestedCount" + comment_id);
      nestedCountSpan.text(response.nested_count);
    },
    error: function () {
      // 에러 처리
    },
  });
}