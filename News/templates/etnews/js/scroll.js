/**
* @package Helix3 Framework
* @author Enginetemplates http://www.enginetemplates.com
* @copyright Copyright (c) 2010 - 2018 Enginetemplates
* @license http://www.gnu.org/licenses/gpl-2.0.html GNU/GPLv2 or later
*/

jQuery(function($){
    var $body = $('body'),
    $wrapper = $('.body-innerwrapper'),
    $toggler = $('#offcanvas-toggler'),
    $close = $('#sp-main-body'),
    $offCanvas = $('.offcanvas-menu');

    var offCanvasShow = function(){
        $body.addClass('offcanvas');
        $wrapper.on('click',offCanvasClose);
        $close.on('click',offCanvasClose);
        $offCanvas.on('click',stopBubble);
    };
    
    var offCanvasClose = function(){
        	$body.removeClass('offcanvas');
        	$wrapper.off('click',offCanvasClose);
        	$close.off('click',offCanvasClose);
        	$offCanvas.off('click',stopBubble);
    };
     $close.on('click', function(event){
        	
        	offCanvasClose();
   });


    var stopBubble = function (e) {
        e.stopPropagation();
        return true;
    };
    
    //scrollspy
    $('[data-spy="scroll"]').each(function () {
        var $spy = $(this).scrollspy('refresh')
    });
  
    $(".offcanvas-inner a").click(function(){
        offCanvasClose();
    });

});