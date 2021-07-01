jQuery(function($){
	$('.qx-element-contact-form form').on('submit',function(event){
		event.preventDefault();
		var $self=$(this);
		var value=$(this).serializeArray();
		$.ajax({
			type:'post',
			data:value,
			beforeSend:function(){
				$self.find('.qx-btn').attr('disabled','disabled');
				$self.find('input, textarea').attr('disabled','disabled');
				$self.find('#qx-element-contact-form-msg').html('');
			},
			success:function(response){

				// Render the message
				if($.parseJSON(response).success)
				{
					$self.find("input[type=text], input[type=email], textarea").val("");
					$self.find('input, textarea').removeAttr('disabled');
					$self.find('#qx-element-contact-form-msg').html($.parseJSON(response).data).fadeIn();
				} 
				else 
				{
					$self.find('#qx-element-contact-form-msg').html($.parseJSON(response).message).fadeIn();
					$self.find('.qx-btn').removeAttr('disabled');
					$self.find('input, textarea').removeAttr('disabled');
				}
			},
			error:function(jqXHR, response) 
			{
				$self.find('#qx-element-contact-form-msg').html(response);
				$self.find('.qx-btn').removeAttr('disabled');
				$self.find('input, textarea').removeAttr('disabled');
			}
		});
	});
});
