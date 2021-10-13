function insertCard($container, suit, number) {
    $li = $('<li><span class="card rank-' + number.toLowerCase() + ' ' + suit + '"></span></li>');
    $li.find('span')
        .append('<span class="rank">' + number + '</span>')
        .append('<span class="suit">&' + suit + 'uit;</span>').data('suit', suit);
    $li.insertBefore($container.find('.card-add-li'));
}

$('.card-add .suits span').click(function(event) {
    event.preventDefault();
    $(this).parent().find('span').removeClass('active');
    $(this).addClass('active');
});

$('.card-add .numbers span').click(function(event) {
    var $suits = $(this).closest('.card-add').find('.suits');
    var suit = $suits.find('span.active').data('suit');
    if (suit) {
        $suits.find('span').removeClass('active');
        var $elem = $(this);
        $elem.addClass('active');
        window.setTimeout(function() {
            $elem.removeClass('active');
        }, 100);
        insertCard($(this).closest('ul'), suit, $(this).text());
    }
});