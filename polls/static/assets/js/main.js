
$(document).ready(function(){

    $(".identifyingClass").click(function () {
        $("#btn_order_edit").attr({hidden:true});
        $("#btn_order_cancel").attr({hidden:false});
        var my_id_value = $(this).data('id');    
        var title =$(this).data('title');     
        $("#btn_order_cancel").data('cancel-id', my_id_value);
        $(".h2-title").html('Do you cancel "'+title+'" buy order?')
        $('.main-modal').show(); 
      
    }); 
    $(".identifyingClass_edit").click(function () {
       
        var my_id_value = $(this).data('id');
        var goods_id=$(this).data('goods_id')    
        var title =$(this).data('title');    
        console.log(goods_id,my_id_value); 
        $("#btn_order_edit").data('edit-id', my_id_value);
        $("#btn_order_edit").data('goods_id',goods_id);
        $(".h2-title").html('Do you update "'+title+'" price ?')
        $('.main-modal').show(); 
        $("#btn_order_edit").attr({hidden:false});
        $("#btn_order_cancel").attr({hidden:true});
    });  
  
    $("#close-modal").click(function () {
        $('.main-modal').hide();
        
    });
    $("#btn_order_cancel").click(function () {
        var id = $(this).data('cancel-id');
        console.log(id);
        $.ajax({
            url: "delete/"+id,
            datatype: 'json',
            type: 'GET',
           
            success: function(data) {
                console.log(data)
               if(data['code']=="OK"){
                var elem = document.querySelector('[data-item="'+id +'"]')       
                elem.parentNode.removeChild(elem);  }   
             }
        });
        $('.main-modal').hide();
        
        $("#btn_order_cancel").removeAttr('data-cancel-id');
       
       
    });
    $("#btn_order_edit").click(function () {
        var id = $(this).data('edit-id');
        var goods_id=$(this).data('goods_id')
        window.location.reload()
        console.log(id);
        $.ajax({
            url: "edit/"+id+"/"+goods_id,
            datatype: 'json',
            type: 'GET',
           
            success: function(data) {
                console.log(data)
               if(data['code']=="OK"){
                window.location.reload()
               }
                // var elem = document.querySelector('[data-item="'+id +'"]')       
                // elem.parentNode.removeChild(elem);  }   
             }
        });
        $('.main-modal').hide();
        
        $("#btn_order_cancel").removeAttr('data-edit-id');
       
       
    });
 
})