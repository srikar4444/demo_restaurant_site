$(document).ready(function(){

  // Contact Form handler
  var contactForm = $(".contact-form");
  var contactFormMethod = contactForm.attr("Method");
  var contactFormEndpoint = contactForm.attr("action");
  

  function displaySubmitting(submitBtn, defaultText, doSubmit) {
    if(doSubmit) {
      submitBtn.addClass("disabled");
      submitBtn.html("<i class='fa fa-spinner'></i> Sending...");
    } else {
      submitBtn.removeClass("disabled");
      submitBtn.html(defaultText);
    }
  }

  contactForm.submit(function(event){
    event.preventDefault();
    var contactFormData = contactForm.serialize();
    var contactFormSubmitBtn  = contactForm.find("[type ='submit']")
    var contactFormSubmitBtnTxt = contactFormSubmitBtn.text()
    var thisForm = $(this);
    displaySubmitting(contactFormSubmitBtn, "",true);
    $.ajax({
      method : contactFormMethod,
      url : contactFormEndpoint,
      data : contactFormData,
      success : function(data){
        //contactForm[0].reset();
        thisForm[0].reset();
        $.alert({
          title: "Success",
          content : data.message,
          theme : "modern",
        });
        setTimeout(function() {
          displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt,false)
        }, 500);
      },
      error: function(data) {
        console.log(data.responseJSON);
        var jsonData = data.responseJSON;
        var msg = "";
        $.each(jsonData, function(key,value) { 
        // jsonData is actually a dict so we use key,value instead of index / object, value
          msg += key + ":" + value[0].message + "<br/>";
        }) ;
        $.alert({
          title: "Oops!",
          content : msg,
          theme : "modern",
        });
        setTimeout(function() {
          displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt,false)
        }, 500);
      },
    });
  })

  // Contct Form handler end

  //Auto Search
  var searchForm = $(".search-form");
  var searchInput = searchForm.find("[name='q']");  // input name = 'q' in the form
  var typingTimer ;
  var typingInterval = 1500 ;// 1.5 seconds as it is in milliseconds
  var searchBtn = searchForm.find("[type='submit']")
  searchInput.keyup(function(event){
    //key relesed
    //console.log(event);
    //ClearTimeout and setTimeout are js functions 
    // setTimeout calls the function defined in it after mentioned timeinterval
    clearTimeout(typingTimer);
    typingTimer = setTimeout(performSearch, typingInterval);
  })

  searchInput.keydown(function(event) {
    //keypressed
    clearTimeout(typingTimer)
  });

  function displaySearching() {
    // changes the search button to searching... and adds a fa-icon
    searchBtn.addClass("disabled");
    searchBtn.html("<i class='fa fa-spinner'></i>Searching...");
  }

  function performSearch() {
    //called to perform search
    displaySearching();
    var query = searchInput.val();
    //console.log(searchInput.val());
    setTimeout(function(){
      window.location.href = '/search/?q=' + query;
    }, 1000);          
  }
  //End of AutoSearch


  // Cart+ Add products
  // this function is to update the items in cart when something is added to cart, without reloading the whole page
  // this works when both product is added or removed from the cart
  // the below thing in brackets is a class value for the form in update-cart.html
  var productForm = $(".form-product-ajax");

  productForm.submit(function(event){
    event.preventDefault();
    //console.log("Form is not sending");
    var thisForm = $(this);  // this is actually used to take data of only one class that we are referring to at that point
    //var actionEndpoint = thisForm.attr("action");  //this points to the url
    var actionEndpoint = thisForm.attr("data-endpoint");
    var httpMethod = thisForm.attr("method");
    var formData = thisForm.serialize();

    // passing using the ajax
    $.ajax({
      url: actionEndpoint,
      method : httpMethod,
      data: formData,
      success : function(data)
      {
        //console.log("success");
        //console.log(data);
        var submitSpan = thisForm.find(".submit-span")
        //console.log(submitSpan.html())
        if (data.added) {
          submitSpan.html('<button class="btn btn-warning" type="submit">Remove from Cart</button>')
        } else {
          submitSpan.html('<button class="btn btn-success" type="submit">Add to Cart</button>')
        }
        //updating the cart items count
        var navbarCartCount = $(".navbar-cart-count");
        navbarCartCount.text( data.cartItemCount);

        // to update the cart display when in cart page
        var currentPath = window.location.href;
        console.log(currentPath)
        // below if condition is not working just check why else is provided for this then it will work
        if (currentPath.indexOf("carts") != -1 ) {
          console.log("in if");
          refreshCart();
        }
        else
        {
          refreshCart();
        }

      },
      error : function(errorData){
        
        //alert("An error occurred");
        $.alert({
          // $.alert is using jquery-coonfirm we can directly use just alert
          title : "Warning!",
          content: "An error occurred",
          theme : "modern"
        });
        //console.log("error");
        //console.log(errorData);
      }
    });
  })

  function refreshCart(){
    // function to update the display of Cart when in cart page
    //console.log("in current cart");
    var cartTable = $(".cart-table");
    // as cart-body is related to cart-table so we are finding it in that itself if one thing is wrong other will be wrong
    var cartBody = cartTable.find(".cart-body");
    //cartBody.html("<h1>Changed</h1>");
    //var productRows = cartBody.find(".cart-products");
    var productRows = cartBody.find(".cart-product");
    var currentUrl = window.location.href;

    var refreshCartUrl = "/api/cart/";
    var refreshCartMethod = "GET";
    var data = {};
    $.ajax ({
      url : refreshCartUrl,
      method : refreshCartMethod,
      data : data,
      success : function(data) {
        console.log("success");
        console.log(data);
        var hiddenCartItemRemoveForm = $(".cart-item-remove-form")
        if(data.products.length > 0) {
          //productRows.html("<tr><td colspan=3>Coming soon</td></tr>");
          productRows.html("");
          i =data.products.length;
          $.each(data.products,function(index,value) {
            console.log(value);
            var newCartItemRemove = hiddenCartItemRemoveForm.clone();
            newCartItemRemove.css("display","block");
            // if we had a class like that then newCartItemRemove.removeClass("hidden-class");
            newCartItemRemove.find(".cart-item-product-id").val(value.id)
            cartBody.prepend("<tr><th scope=\"row\">" + i +"</th><td><a href='" + value.url + "'>" + value.name + "</a>" +newCartItemRemove.html()+ "</td><td>" + value.price + "</td>"+ "<td>" + 1 + "</td></tr>");
            i--;
          })

          cartBody.find(".cart-subtotal").text(data.subtotal);
          cartBody.find(".cart-total").text(data.total);
        } else {
          window.location.href = currentUrl;
        }

      },
      error : function(errorData) {

        //$.alert("An error occurred");
        //console.log("error");
        //console.log(errorData)
        // jquery-confirm is used in the below alert
        $.alert({
          // $.alert is using jquery-coonfirm we can directly use just alert
          title : "Warning!",
          content: "An error occurred",
          theme : "modern"
        });
      }

    });
  }
})