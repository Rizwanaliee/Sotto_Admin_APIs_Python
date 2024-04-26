jQuery("#admin-login-page-form").validate({
    rules:{
        email:{
            required:true,
            email:true
        },
        password:"required"
    },messages:{
        email:{
            required:"Please Enter Email",
            email:"Please Enter A Valid Email"
        },
        password:"Please Enter Your Password"
    }
});

jQuery("#change-password-form").validate({
    rules:{
        new_pass:"required",
        confirm_new_pass:"required"
    },messages:{
        new_pass:"Please Password",
        confirm_new_pass:"Please Enter Confirm Password"
    }
});

jQuery("#cust_send_notify_form").validate({
    rules:{
        title:{
            required:true,
            maxlength:100
        }, 
        message:{
            required:true,
            maxlength:250
        }
    },messages:{
        title:{
            required:"Please Enter Title",
            maxlength:"Max length should be 100 characters"
        },
        message:{
            required:"Please Enter Message",
            maxlength:"Max length should be 250 characters"
        }
    }
});

jQuery("#setting-form").validate({
    rules:{
        providerFee:{
            required:true,
            digits: true
        },
        patinetMinPrice:{
            required:true,
            digits: true
        },
        patientMaxPrice:{
            required:true,
            digits: true
        }
    },messages:{
        providerFee:{
            required:"Please Enter Fee",
            digits:"Please Enter Only Decimal Digits"
        },
        patinetMinPrice:{
            required:"Please Enter Patient Minimum Price",
            digits:"Please Enter Only Decimal Digits"
        },
        patientMaxPrice:{
            required:"Please Enter Patient Maximum Price",
            digits:"Please Enter Only Decimal Digits"
        }
    }
});

jQuery("#banner-add-form").validate({
    rules:{
        title:{
            required:true,
            maxlength:100
        }, 
        bannerImage:"required"
    },messages:{
        title:{
            required:"Please Enter Title",
            maxlength:"Max length should be 100 characters"
        },
        bannerImage:"Please Upload Banner Image"
    }
});


