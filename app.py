from flask import Flask, request, abort, render_template,redirect

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton
)
import os
import datetime

#アクセスキーの取得
app = Flask(__name__)
#Botの認証
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("callback",methods=['POST'])
def callback():
    signature = request.handlers['X-Line-Signature']
    body = request.get_data(app_text = True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print(" %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#テキストメッセージが送られたときのイベント
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    #日付型で日付データを取得
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    day_before_yesterday = today - timedelta(days=2)

    #日付型→文字列型
    td_date = datetime.datetime.strftime(now_date, '%Y-%m-$d')
    yd_date = datetime.datetime.strftime(yesterday, '%Y-%m-$d')
    dby_date = datetime.datetime.strftime(day_before_yesterday, '%Y-%m-$d')

    #dby、yd、td、totalの定義
    dby = 0
    yd = 0
    td = 0
    total = 0

    #ユーザーから貯金額に関するメッセージが贈られてきた時のイベント
    if text in '貯金額':
        #DBにアクセスしてデータを取得する
        sql = "SELECT SUM(value) FROM;"#GROUP BY とかはご自由に。
        with conn.cursor() as cur:
            cur.execute(sql)


        #dby=一昨日のデータ、yd=昨日のデータ、td=今日のデータ、total=合計貯金額
        buble = BubbleContainer(
            #左から右に文章が進むように設定
            direction = 'ltr',
            body = BoxComponent(
                layot = 'vertical',
                contents = [
                    #title
                    TextComponent(text = '3日間の貯金額',weight = 'bold',size = 'xxl'),
                    SeparatorComponent(margin = 'xxl'),
                    #three days money
                    BoxComponent(
                        layout = 'vertical',
                        margin = 'xxl',
                        contents = [
                            #money of the day before yesterday
                            BoxComponent(
                                layout = 'baseline',
                                contents = [
                                    TextComponent(text = '一昨日',size = 'sm',flex = '0',color = '#555555'),
                                    TextComponent(text = str(dby)+'円',size = 'sm',align = 'end',color = '#111111')
                                ],
                            ),
                            #money of the yesterday
                            BoxComponent(
                                layout = 'baseline',
                                contents = [
                                    TextComponent(text = '昨日',size = 'sm',flex = '0',color = '#555555'),
                                    TextComponent(text = str(yd)+'円',size = 'sm',align = 'end',color = '#111111')
                                ],
                            ),
                            #money of the today
                            BoxComponent(
                                layout = 'baseline',
                                contents = [
                                    TextComponent(text = '今日',size = 'sm',flex = '0',color = '#555555'),
                                    TextComponent(text = str(td)+'円',size = 'sm',align = 'end',color = '#111111')
                                ],
                            ),
                        ],
                    ),
                    SeparatorComponent(margin = 'xxl'),
                    #total money
                    BoxComponent(
                        layout = 'baseline',
                        contents = [
                            TextComponent(text = '合計貯金額',size = 'sm',flex = '0',color = '#555555'),
                            TextComponent(text = str(total)+'円',size = 'sm',align = 'end',color = '#111111')
                        ],
                    ),
                    SeparatorComponent(margin = 'xxl'),
                ]
            ),
            footer = BoxComponent(
                layout = 'vertical',
                spacing = 'sm',
                #link for our website
                ButtonComponent(
                style = 'link',
                height = 'sm',
                action = URIAction(label = '公式サイト',uri='')
                )
            )
        )

    #ユーザーからヘルプを表示してほしいとメッセージが送られたときのイベント
    elif text in 'ヘルプ':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text = '貯金額が知りたい。\n→「貯金額」と送信する。',
            )
        )

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text = 'ごめんなさい。\nそのメッセージに対応する返信は用意されていません。\n対応しているメッセージについては、「ヘルプ」とメッセージを送って参照してください。',
            )
        )

#その他のメッセージへの対応
@handler.add(MessageEvent, message=(LocationMessage, StickerMessage, ImageMessage, VideoMessage, AudioMessage))
def handle_other_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text = 'ごめんなさい。\nこのアカウントはユーザー様とテキストメッセージを使ってやり取りを行うアカウントです。\n対応しているメッセージについては、「ヘルプ」とメッセージを送って参照してください。',
        )
    )
#友達追加したときのイベント
@handler.add(FollowEvent)
def handle_follow(event):
    UserID = event.source.user_id
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='友達追加ありがとう！\n貯金額を知りたい場合は、「貯金額」とメッセージを送ってね。\nヘルプを表示したい場合は、「ヘルプ」とメッセージを送ってね。',
        )
    )

#ブロックされたときのイベント
@handler.add(UnfollowEvent)
def handle_unfollow(event):
    UseID = event.source.user_id
    #UserIDをデータベースから削除する

conn = psycopg2.connect('dbname=dd7kbsbiacro6l host=ec2-75-101-131-79.compute-1.amazonaws.com user=grkxppqvrlmwts password=2f92dae80cd0543e3b2c7af59c631e86ae7d2353b7f4e6a384213d6229e74674')
conn.autocommit = True

@app.route('/insert/',methods=['POST']) 
def insert():
    value = request.form['value']#大括弧なのに注意。
    insert_column(value)
    return "Insert done." #Noneを返すとstatus code が500になる。

def insert_column(value):
    sql = "INSERT INTO record(value,updated_at) VALUES({},current_date)".format(value)
    with conn.cursor() as cur:
        cur.execute(sql)



if __name__ == '__main__':
    app.run()
