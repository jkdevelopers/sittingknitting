$(document).ready(function () {
    $('#cssmenu > ul > li > a').click(function () {
        $('#cssmenu li').removeClass('active');
        $(this).closest('li').addClass('active');
        var checkElement = $(this).next();
        if ((checkElement.is('ul')) && (checkElement.is(':visible'))) {
            $(this).closest('li').removeClass('active');
            checkElement.slideUp('normal');
        }
        if ((checkElement.is('ul')) && (!checkElement.is(':visible'))) {
            $('#cssmenu ul ul:visible').slideUp('normal');
            checkElement.slideDown('normal');
        }
        if ($(this).closest('li').find('ul').children().length == 0) {
            return true;
        } else {
            return false;
        }
    });
});


// Login Form
$(function () {
    var button = $('#loginButton');
    var box = $('#loginBox');
    var form = $('#loginForm');
    button.removeAttr('href');
    button.mouseup(function (login) {
        box.toggle();
        button.toggleClass('active');
    });
    form.mouseup(function () {
        return false;
    });
    $(this).mouseup(function (login) {
        if (!($(login.target).parent('#loginButton').length > 0)) {
            button.removeClass('active');
            box.hide();
        }
    });
});

// Custom menu
$(document).ready(function () {
    $('.megamenu [data-color]').hover(function (e) {
        $(this).css(
            'background',
            e.type === 'mouseenter' ? $(this).attr('data-color') : 'inherit'
        );
    });
    $('.megamenu li.grid > a').click(function (e) {
        var single = $(this).parent().children().length;
        if (single == 1) return;
        e.preventDefault();
    });
});

// Phone field & messages close button
$(document).ready(function () {
    $('input[name$=phone]').mask('+7 (999) 999-99-99');
    $('a[data-dismiss=alert]').click(function () {
        $(this).parent().remove();
    });
});

// Subscribe form
$(document).ready(function () {
    $('#subscribe').submit(function (e) {
        e.preventDefault();
        var form = $('#subscribe');
        $.post(form.attr('action'), form.serialize(), function (data) {
            if (data !== 'OK') {
                form.find('.errors').html(data);
            } else {
                form.find('*').hide();
                form.find('.thanks').show();
            }
        })
    });
});

// Order form
$(document).ready(function () {
    $('#order-form select').change(function (e) {
        var value = $('#order-form select').val();
        var url = $('#order-form').attr('data-dcu').replace('_', value);
        window.location = url;
    });
    $('.cpns').click(function () {
        var value = $('#order-form input[name=coupon]').val().replace(/\s+/g, '');
        if (value.length == 0) return;
        var url = $('.cpns').attr('data-ccu').replace('_', value);
        window.location = url;
    });
});

// Scroll to anchor
$(document).ready(function () {
    $('[data-scroll-to]').click(function (e) {
        e.preventDefault();
        var target = $($(this).attr('data-scroll-to'));
        $('html, body').animate({scrollTop: target.offset().top}, 'slow');
    });
});

// Misc
$(document).ready(function () {
    $('.email-link').attr('href', 'mailto:' + $('.email-link').text().trim());
    if ($(window).width() < 700) $('.stay form input[type="email"]').attr('placeholder', 'Введите email');


    // Галочка в регистрации
    $('input[name=accept]').change(function () {
        console.log($(this)[0].checked);
        if ($(this)[0].checked) $('#register-submit').show();
        else $('#register-submit').hide();
    });

    // Выбор модификаций
    $('.btn_form select').change(function(e) {
        var selector = '[data-mod=' + $(this).val() + '] .product_price a';
        var button = $(selector).clone();
        $('.btn_form a').replaceWith(button);
    });

    // Фильтры

    var params = new URLSearchParams(window.location.search);
    var raw = (params.get('filter') || '');
    var groups = raw.split('|').map(x => x.split(','));
    var filter = groups.map(x => x.filter(y => y.length).map(y => +y));

    function update() {
        var raw = filter.map(x => x.join(',')).join('|');
        params.set('filter', raw);
        var url = window.location.pathname + '?' + params.toString();
        window.location = url;
    }

    $('.filter-group a[data-value]').click(function () {
        var state = !!$(this).find('input').attr('checked');
        var value = +$(this).attr('data-value');
        var group = +$(this).parent().attr('data-value');
        var delta = group - filter.length + 1;
        if (delta > 0) for (var i = 0; i < delta; i++) filter.push([]);
        if (state) filter[group] = filter[group].filter(x => x != value);
        else filter[group].push(value);
        update();
    });

    // Сортировки

    $('.sortings a').click(function () {
        if ($(this).hasClass('active')) return;
        params.set('sorting', $(this).attr('data-value'));
        update();
    });
});
