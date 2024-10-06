import pandas as pd
import matplotlib as mpl
from matplotlib.pyplot import *
from operator import itemgetter

mpl.use('pgf')
mpl.rcParams.update({
    'font.family': 'serif',
    'font.size': 10.5,
    'pgf.rcfonts': False,
    'text.usetex': True,
    'pgf.preamble': '\n'.join([
        r"\usepackage{unicode-math}",
        r"\setmathfont{XITS Math}",
        r"\setmainfont{Times New Roman}",
        r"\usepackage{xeCJK}",
        r"\xeCJKsetup{CJKmath=true}",
        r"\setCJKmainfont{SimSun}", ])})
SAVEAS = 'output.xlsx'


def cal_gpa(d):
    return (d['课程学分'] * d['绩点']).sum() / d['课程学分'].sum()


def query_by_name(df, name, num):
    d = df[df['学号'] == np.int64(name)] if num else df[df['姓名'] == name]
    gpa_data = d.groupby(['学年度', '学期'], include_groups=False).apply(cal_gpa).to_dict()
    gpa_data['总GPA'] = cal_gpa(d)
    return {f"{k[0]}{k[1]}" if isinstance(k, tuple) else k: v for k, v in gpa_data.items()}, d


def picture(df, title_, alpha=0.6, fontsize=7, color='red', linestyle='--', ver=-0.1):
    hist(list(df.values()), bins=len(df)//3, alpha=alpha)
    xlim(0, 5)
    for i in np.linspace(0, 100, 5 + 1)[1:-1]:
        q = np.quantile(list(df.values()), i / 100)
        axvline(x=q, color=color, linestyle=linestyle)
        text(q, ver, f'{q:.2f}', fontsize=fontsize, ha='center', va='top', color=color)
    title(title_)
    savefig(title_ + '.png')
    close()



data = pd.read_parquet('data')
if input('保存各专业绩点分布直方图？（确认打Y）') == 'Y':
    list(map(picture,
             [dict(sorted(
                 {n: cal_gpa(g.fillna(0)) for n, g in data[data['班级'].isin(c)].groupby('姓名')}.items(),
                 key=itemgetter(1), reverse=True))
                 for c in {1: ['工业智能2201', '工业智能2202'],
                           2: [f'自动化220{i}' for i in range(1, 7)],
                           3: ['自动化2201（强基班）'],
                           4: ['测控2201', '测控2202'],
                           5: ['电科2201', '电科2202'],
                           6: ['电气2201', '电气2202']}.values()],
             ['工业智能', '自动化', '强基', '测控', '电科', '电气']))

r = []
for n in input('姓名或学号（多个查询用空格分隔）').split():
    if n.isdigit(): n = np.int64(n)

    gpa_data, d = query_by_name(data, n, type(n) == np.int64)
    for s, gpa in gpa_data.items():
        print(f'{s}\t{gpa: .6f}')
    r.append(d)

to = input(f'数据导出至（按回车到默认位置{SAVEAS}）')
pd.concat(r, axis=0, ignore_index=True).to_excel(to if len(to) else SAVEAS)
