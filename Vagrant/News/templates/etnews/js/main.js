/**
* @package Helix3 Framework
* @author Enginetemplates http://www.enginetemplates.com
* @copyright Copyright (c) 2010 - 2018 Enginetemplates
* @license http://www.gnu.org/licenses/gpl-2.0.html GNU/GPLv2 or later
*/
jQuery(function($) {
    $('#offcanvas-toggler').on('click', function(event){
        event.preventDefault();
        $('body').toggleClass('offcanvas');
    });

    $('.close-offcanvas').on('click', function(event){
        event.preventDefault();
        $('body').removeClass('offcanvas');
    });

    //Mega Menu
    $('.sp-megamenu-wrapper').parent().parent().css('position','static').parent().css('position', 'relative');
    $('.sp-menu-full').each(function(){
        $(this).parent().addClass('menu-justify');
    });

    //Sticky Menu
    $(document).ready(function(){
    	$("body.sticky-header").find('#sp-header').sticky({topSpacing:0})
    });
  
     $( ".offcanvas-inner ul li a" ).click(function() {
            offCanvasClose();
     });

    //Tooltip
    $(function () {
      $('[data-toggle="tooltip"]').tooltip()
    });

});