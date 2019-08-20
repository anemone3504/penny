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
from dateutil.relativedelta import relativedelta
import os
import datetime
import psycopg2
import contentsGenerator

#アクセスキーの取得
app = Flask(__name__)
#Botの認証
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback",methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text = True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

handler.add(PostbackEvent)
def handle_postback(event):
    #今日の日付データを取得
    x = datetime.date.today()

    #DBにアクセスして累計貯金額を取得
    sql = "SELECT SUM(value) FROM record"
    with conn.cursor() as cur:
        cur.execute(sql)
        total_results = cur.fetchall()

    if event.postback.data == '1週間':
        #1週間前の日付を取得
        purpose_date = x - datetime.timedelta(weeks = 1)
        purpose_date = purpose_date.isoformat()

        #DBにアクセスしてデータを取得する
        sql = f"SELECT updated_at, SUM(value) FROM record WHERE updated_at > '{purpose_date}' GROUP BY updated_at ORDER BY updated_at ASC;"#GROUP BY とかはご自由に。
        with conn.cursor() as cur:
            cur.execute(sql) #executeメソッドでクエリを実行。
            one_week_results = cur.fetchall()  #fetchall
        #results は 以下のようなデータフォーマットである.
        #[(1行目の1列目の属性,1行目の2列目の属性,...,1行目のn列目の属性),(2行目の1列目の属性,...,2行目のn列目の属性),...,(m行目の1列目,...,m行目のn列目)]
        #そして、m行目のn列目のアクセスしたい場合は
        #results[m-1][n-1] で可能である。

        #こういうのも便利かも？
        #for column in cur.ferchall():
        #   anycode...
        #で１行ずつタプルで情報を取り出せる。

        #使用しているテーブル情報を以下に示す。
        # 表:record (
            # 属性:id int型 auto_increment PRIMARY KEY NOT NULL, //一意性の保持のための属性
            # 属性:value int型 //金額の情報
            # 属性:updated_at date型 //日日の情報のみが含まれている。時刻に関する情報は含まれていない。
        # )

        bubble = BubbleContainer(
            #左から右に文章が進むように設定
            direction = 'ltr',
            body = BoxComponent(
                layout = 'vertical',
                contents = [
                    #title
                    TextComponent(text = '1週間の貯金額',weight = 'bold',size = 'xxl'),
                    SeparatorComponent(margin = 'lg'),
                    #three days money
                    BoxComponent(
                        layout = 'vertical',
                        margin = 'lg',
                        contents = contentsGenerator.gen(len(one_week_results),one_week_results)
                    ),
                    SeparatorComponent(margin = 'lg'),
                    #total money
                    BoxComponent(
                        layout = 'baseline',
                        margin = 'lg',
                        contents = [
                            TextComponent(text = '累計貯金額',size = 'sm',flex = 1,color = '#555555'),
                            TextComponent(text = str(total_results[0][0])'円',size = 'sm',align = 'end',color = '#111111')
                        ],
                    )
                ],
            ),
        )
        message = FlexSendMessage(alt_text = "1週間の貯金額", contents = bubble)
        line_bot_api.reply_message(
            event.reply_token,
            message
                quick_reply = QuickReply(
                    items = [
                        QuickReplyButton(
                            action = PostbackAction(label = "1週間分の貯金額",data = "1週間")
                        ),
                        QuickReplyButton(
                            action = PostbackAction(label = "1ヶ月分の貯金額",data = "1ヶ月")
                        ),
                        QuickReplyButton(
                            action = PostbackAction(label = "1年分の貯金額",data = "1年分")
                        )
                    ]
                )
        )

    elif event.postback.data == '1ヶ月':
        #1ヶ月前の日付を取得
        purpose_date = x - relativedelta(months = 1)
        purpose_date = purpose_date.isoformat()

        #DBにアクセスしてデータを取得
        sql = f"SELECT SUM(value) FROM record WHERE updated_at > '{purpose_date}';"#GROUP BY とかはご自由に。
        with conn.cursor() as cur:
            cur.execute(sql) #executeメソッドでクエリを実行。
            one_month_results = cur.fetchall()
        bubble = BubbleContainer(
            #左から右に文章が進むように設定
            direction = 'ltr',
            body = BoxComponent(
                layout = 'vertical',
                contents = [
                    #title
                    TextComponent(text = '1ヶ月の貯金額',weight = 'bold',size = 'xxl'),
                    SeparatorComponent(margin = 'lg'),
                    #three days money
                    BoxComponent(
                        layout = 'vertical',
                        margin = 'lg',
                        contents = [
                            BoxComponent(
                                layout = 'baseline',
                                contents = [
                                    TextComponent(text = '今月',size = 'xl',flex = 1,color = '#555555'),
                                    TextComponent(text = str(one_month_results[0][0]) + '円',size = 'xl',align = 'end',color = '#111111')
                                ]
                            )
                        ]
                    ),
                    SeparatorComponent(margin = 'lg'),
                    #total money
                    BoxComponent(
                        layout = 'baseline',
                        margin = 'lg',
                        contents = [
                            TextComponent(text = '累計貯金額',size = 'sm',flex = 1,color = '#555555'),
                            TextComponent(text = str(total_results[0][0])'円',size = 'sm',align = 'end',color = '#111111')
                        ],
                    )
                ],
            ),
        )
        message = FlexSendMessage(alt_text = "1ヶ月の貯金額", contents = bubble)
        line_bot_api.reply_message(
            event.reply_token,
            message,
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = PostbackAction(label = "1週間分の貯金額",data = "1週間")
                    ),
                    QuickReplyButton(
                        action = PostbackAction(label = "1ヶ月分の貯金額",data = "1ヶ月")
                    ),
                    QuickReplyButton(
                        action = PostbackAction(label = "1年分の貯金額",data = "1年分")
                    )
                ]
            )
        )

    elif event.postback.data == '1年':
        #1年前の日付を取得
        purpose_date = x - relativedelta(years = 1)
        purpose_date = purpose_date.isoformat()

        #DBにアクセスしてデータを取得
        sql = f"SELECT SUM(value) FROM record WHERE updated_at > '{purpose_date}';"#GROUP BY とかはご自由に。
        with conn.cursor() as cur:
            cur.execute(sql) #executeメソッドでクエリを実行。
            one_year_results = cur.fetchall()
        bubble = BubbleContainer(
            #左から右に文章が進むように設定
            direction = 'ltr',
            body = BoxComponent(
                layout = 'vertical',
                contents = [
                    #title
                    TextComponent(text = '1年間の貯金額',weight = 'bold',size = 'xxl'),
                    SeparatorComponent(margin = 'lg'),
                    #three days money
                    BoxComponent(
                        layout = 'vertical',
                        margin = 'lg',
                        contents = [
                            BoxComponent(
                                layout = 'baseline',
                                contents = [
                                    TextComponent(text = '今年',size = 'xl',flex = 1,color = '#555555'),
                                    TextComponent(text = str(one_year_results[0][0]) + '円',size = 'xl',align = 'end',color = '#111111')
                                ]
                            )
                        ]
                    ),
                    SeparatorComponent(margin = 'lg'),
                    #total money
                    BoxComponent(
                        layout = 'baseline',
                        margin = 'lg',
                        contents = [
                            TextComponent(text = '累計貯金額',size = 'sm',flex = 1,color = '#555555'),
                            TextComponent(text = str(total_results[0][0])'円',size = 'sm',align = 'end',color = '#111111')
                        ],
                    )
                ],
            ),
        )
        message = FlexSendMessage(alt_text = "1年の貯金額", contents = bubble)
        line_bot_api.reply_message(
            event.reply_token,
            message,
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = PostbackAction(label = "1週間分の貯金額",data = "1週間")
                    ),
                    QuickReplyButton(
                        action = PostbackAction(label = "1ヶ月分の貯金額",data = "1ヶ月")
                    ),
                    QuickReplyButton(
                        action = PostbackAction(label = "1年分の貯金額",data = "1年分")
                    )
                ]
            )
        )

#テキストメッセージが送られたときのイベント
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    #ユーザーからヘルプを表示してほしいとメッセージが送られたときのイベント
    elif text == 'ヘルプ':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text = '俺からしてやれることは何もない。',
                quick_reply = QuickReply(
                    items = [
                        QuickReplyButton(
                            action = PostbackAction(label = "1週間分の貯金額",data = "1週間")
                        ),
                        QuickReplyButton(
                            action = PostbackAction(label = "1ヶ月分の貯金額",data = "1ヶ月")
                        ),
                        QuickReplyButton(
                            action = PostbackAction(label = "1年分の貯金額",data = "1年")
                        )
                    ]
                )
            )
        )

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text = 'ごめんなさい。\nそのメッセージに対応する返信は用意されていません。\n対応しているメッセージについては、「ヘルプ」とメッセージを送って参照してください。',
                quick_reply = QuickReply(
                    items = [
                        QuickReplyButton(
                            action = PostbackAction(label = "1週間分の貯金額",data = "1週間")
                        ),
                        QuickReplyButton(
                            action = PostbackAction(label = "1ヶ月分の貯金額",data = "1ヶ月")
                        ),
                        QuickReplyButton(
                            action = PostbackAction(label = "1年分の貯金額",data = "1年分")
                        )
                    ]
                )
            )
        )

#その他のメッセージへの対応
@handler.add(MessageEvent, message=(LocationMessage, StickerMessage, ImageMessage, VideoMessage, AudioMessage))
def handle_other_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text = 'ごめんなさい。\nこのアカウントはユーザー様とテキストメッセージを使ってやり取りを行うアカウントです。\n対応しているメッセージについては、「ヘルプ」とメッセージを送って参照してください。',
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = PostbackAction(label = "1週間分の貯金額",data = "1週間")
                    ),
                    QuickReplyButton(
                        action = PostbackAction(label = "1ヶ月分の貯金額",data = "1ヶ月")
                    ),
                    QuickReplyButton(
                        action = PostbackAction(label = "1年分の貯金額",data = "1年分")
                    )
                ]
            )
        )
    )
#友達追加したときのイベント
@handler.add(FollowEvent)
def handle_follow(event):
    UserID = event.source.user_id
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text = "友達追加ありがとう！\n貯金額を確認したいときは下のボタンを押してね",
            quick_reply = QuickReply(
                items = [
                    QuickReplyButton(
                        action = PostbackAction(label = "1週間分の貯金額",data = "1週間")
                    ),
                    QuickReplyButton(
                        action = PostbackAction(label = "1ヶ月分の貯金額",data = "1ヶ月")
                    ),
                    QuickReplyButton(
                        action = PostbackAction(label = "1年分の貯金額",data = "1年分")
                    )
                ]
            )
        )
    )

#ブロックされたときのイベント
@handler.add(UnfollowEvent)
def handle_unfollow(event):
    UseID = event.source.user_id
    #UserIDをデータベースから削除する

conn = psycopg2.connect('dbname=dd7kbsbiacro6l host=ec2-75-101-131-79.compute-1.amazonaws.com user=grkxppqvrlmwts password=2f92dae80cd0543e3b2c7af59c631e86ae7d2353b7f4e6a384213d6229e74674')
conn.autocommit = True

@app.route('/')
def confirm():
    return "penny はしっかり稼働中だよ。"

@app.route('/insert/',methods=['POST'])
def insert():
    value = request.form['value']#大括弧なのに注意。
    insert_column(value)
    return "Insert done." #Noneを返すとstatus code が500になる。

def insert_column(value):
    sql = "INSERT INTO record(value,updated_at) VALUES({},current_date)".format(value)
    with conn.cursor() as cur:
        cur.execute(sql)
if __name__ == "__main__":
    app.run()
