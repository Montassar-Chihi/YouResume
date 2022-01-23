$(function() {
    $(".box").on("mousedown", function(e) {
        const gate = $(this).children("div");
        $(this).children(".locker").hide();
        for (var i = 0; i < gate.length; i++) {
            if ($(gate[i]).hasClass("ovrl-left")) {
                $(gate[i]).toggleClass("move-right");
            }
            if ($(gate[i]).hasClass("ovrl-right")) {
                $(gate[i]).toggleClass("move-left");
            }
        }
        // removes the click event after reveling the image
        $(this).off();
    });
});


// Get the modal
var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal 
btn.onclick = function() {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
        modal.style.display = "none";
    }
    // When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

var modal1 = document.getElementById("myModal1");

// Get the button that opens the modal1
var btn1 = document.getElementById("myBtn1");

// Get the <span> element that closes the modal1
var span1 = document.getElementsByClassName("close1")[0];

// When the user clicks the button, open the modal1 
btn1.onclick = function() {
    modal1.style.display = "block";
}

// When the user clicks on <span> (x), close the modal1
span1.onclick = function() {
        modal1.style.display = "none";
    }
    // When the user clicks anywhere outside of the modal1, close it
window.onclick = function(event) {
    if (event.target == modal1) {
        modal1.style.display = "none";
    }
}

var slideIndex = [1, 1];
var slideId = ["mySlides1", "mySlides2"]
showSlides(1, 0);
showSlides(1, 1);

function plusSlides(n, no) {
    showSlides(slideIndex[no] += n, no);
}

function showSlides(n, no) {
    var i;
    var x = document.getElementsByClassName(slideId[no]);
    if (n > x.length) { slideIndex[no] = 1 }
    if (n < 1) { slideIndex[no] = x.length }
    for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";
    }
    x[slideIndex[no] - 1].style.display = "block";
}