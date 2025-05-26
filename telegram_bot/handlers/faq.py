import texts
from aiogram import Router, F
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, CallbackQuery, \
    InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.db.models import Q
from keyboards.callback_data import BackCallback
from shop_app.models import FAQ
from utils.messages import update_or_send_message

router = Router()


@router.callback_query(BackCallback.filter(F.to == "faq"))
async def show_faq_entry_point(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=texts.FAQ_TRY_BUTTON_TEXT, switch_inline_query_current_chat=""))
    builder.row(InlineKeyboardButton(text=texts.BACK_TO_MENU_BUTTON, callback_data=BackCallback(to="main_menu").pack()))
    keyboard = builder.as_markup()
    await update_or_send_message(
        event=callback,
        text=texts.FAQ_SEARCH_PROMPT_MESSAGE,
        reply_markup=keyboard
    )


@router.inline_query(F.query)
async def inline_faq_search(inline_query: InlineQuery):
    query = inline_query.query.lower().strip()

    if not query:
        results = [
            InlineQueryResultArticle(
                id="empty_query",
                title=texts.FAQ_INLINE_QUERY_PROMPT,
                input_message_content=InputTextMessageContent(
                    message_text=texts.FAQ_INLINE_QUERY_PROMPT,
                    parse_mode="HTML"
                )
            )
        ]
        await inline_query.answer(results, is_personal=True, cache_time=0)
        return

    @sync_to_async
    def get_faq_results(search_query: str):
        qs = FAQ.objects.filter(is_active=True).filter(
            Q(question__icontains=search_query) | Q(keywords__icontains=search_query)
        ).order_by('order')
        return list(qs)

    faq_items = await get_faq_results(query)

    if not faq_items:
        results = [
            InlineQueryResultArticle(
                id="no_results",
                title=texts.FAQ_NO_RESULTS,
                input_message_content=InputTextMessageContent(
                    message_text=texts.FAQ_NO_RESULTS,
                    parse_mode="HTML"
                )
            )
        ]
    else:
        results = []
        for i, item in enumerate(faq_items):
            result_id = f"faq_{item.id}_{i}"
            results.append(
                InlineQueryResultArticle(
                    id=result_id,
                    title=item.question,
                    input_message_content=InputTextMessageContent(
                        message_text=texts.FAQ_QUESTION_ANSWER_TEMPLATE.format(
                            question=item.question,
                            answer=item.answer
                        ),
                        parse_mode="HTML"
                    ),
                    description=item.answer[:100] + "..." if len(item.answer) > 100 else item.answer
                )
            )

    await inline_query.answer(results, is_personal=True, cache_time=0)
