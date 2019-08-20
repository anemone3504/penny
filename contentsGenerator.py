from linebot.models import (
    BoxComponent,
    TextComponent
)

def gen(exist_dates,results):
    #外側の配列
    BoxComponents = []
    for i in range(exist_dates):
        strdate=results[i][0].isoformat()#JSONうんたらがdate型はだめいわれてる？みたいだから文字列変換しますからぁ！
        ele=BoxComponent(
            layout = 'baseline',
            contents = [
                TextComponent(text = strdate,size = 'sm',flex = 1,color = '#555555'),
                TextComponent(text = str(results[i][1]) + '円',size = 'sm',align = 'end',color = '#111111')
            ]
        )

        BoxComponents.append(ele)
    return BoxComponents
