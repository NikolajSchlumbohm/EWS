import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd 
from lifelines import LogLogisticAFTFitter, WeibullAFTFitter
from lifelines import LogNormalAFTFitter
from lifelines import CoxPHFitter
from lifelines import KaplanMeierFitter
from lifelines import LogLogisticAFTFitter
import os
import numpy as np


categories = ["meme","ort","person","politik","text"]
all_semantic_categories = ["meme_person_politik","politik","person_politik","meme_person","meme","ort","person","politik","meme_person"]

def create_normalized_df(data):
    # return a normalized DataFrame where the viewing duration of every image with wordcount > 0 is normalized for that word count
    print(data)
    df = data.copy()
    # parse words column to int
    df["words"] = df["words"].astype(int)
    df = df[df["words"] > 0].copy()
    # Subtract the minimum duration (5 seconds) from each duration
    df["adjusted_duration"] = df["duration"] - 5
    # Normalize by word count
    df["normalized_duration"] = df["adjusted_duration"] / df["words"]
    
    return df

def create_tag_group_dict(data):
    # Create a mapping of tag combinations to image IDs
    tag_group_dict = {}
    df = data.copy()
    for idx, row in df.iterrows():
        category_code = str(int(row['categoryCode'])).zfill(5)
        if category_code not in tag_group_dict:
            tag_group_dict[category_code] = []
        id =     int(row['imageID'])
        if id not in tag_group_dict[category_code]:
            tag_group_dict[category_code].append(id)
    return tag_group_dict

def tag_group_analysis(data):
    df = data.copy()
    tag_group_analysis = []

    for tag_combination, image_ids in create_tag_group_dict(df).items():
        # Filter data for images in this tag group
        tag_group_data = data[data['imageID'].isin(image_ids)]
        
        if not tag_group_data.empty:
            analysis = {
                'tag_combination': tag_combination,
                'tag_string': '_'.join(get_categories(tag_combination)),  # For easier reading
                'image_ids': image_ids,
                'image_count': len(image_ids),
                'total_observations': len(tag_group_data),
                'mean_system_time': tag_group_data['duration'].mean(),
                'median_system_time': tag_group_data['duration'].median(),
                'std_system_time': tag_group_data['duration'].std(),
                'min_system_time': tag_group_data['duration'].min(),
                'max_system_time': tag_group_data['duration'].max()
            }
            tag_group_analysis.append(analysis)
    tag_analysis_df = pd.DataFrame(tag_group_analysis)
    tag_analysis_df = tag_analysis_df.sort_values('median_system_time', ascending=False)
    print("\n" + "="*80)
    print("TAG GROUP ANALYSIS")
    print("="*80)
    
    print(f"Total tag groups found: {len(tag_analysis_df)}")
    print("\nTag groups ranked by mean viewing time:")
    print("-" * 80)
    
    for idx, row in tag_analysis_df.iterrows():
        print(f"Tag Group: {row['tag_string']}")
        print(f"  Images: {row['image_count']} (IDs: {row['image_ids']})")
        print(f"  Observations: {row['total_observations']}")
        print(f"  Mean time: {row['mean_system_time']:.2f}s")
        print(f"  Median time: {row['median_system_time']:.2f}s")
        print(f"  Std dev: {row['std_system_time']:.2f}s")
        print(f"  Range: {row['min_system_time']:.2f}s - {row['max_system_time']:.2f}s")
        print("-" * 40)
    
    return tag_analysis_df

def get_categories(categoryCode):
    categoryCode = str(int(categoryCode)).zfill(5)
    tags = list()
    for i in range(5):
        if categoryCode[i] == '1':
            tags.append(categories[i])
    return tags

def create_view_time_matrix(data):
    view_time_matrix = pd.DataFrame(0, index=all_semantic_categories, columns=["text", "no_text"], dtype=int)
    # for every tag combination in tag_analysis_df["tag_combination"]

    df = data.copy()
    df = df.groupby('categoryCode').agg({'duration': 'median'}).reset_index()
    print(df)

    for idx, row in df.iterrows():
        cur_categories = get_categories(row['categoryCode'])

        if "text" in cur_categories:
            if len(cur_categories) ==1:
                view_time_matrix.at["Nur Text", "text"] = row['duration']
                continue
            cur_categories.remove("text")
            category_string = "_".join(cur_categories)
            view_time_matrix.at[category_string, "text"] = row['duration']
        else:
            category_string = "_".join(cur_categories)
            view_time_matrix.at[category_string, "no_text"] = row['duration']
                
    return view_time_matrix

def plot_view_time_matrix(data):
    view_time_matrix = create_view_time_matrix(data)
        
    plt.figure(figsize=(10, 6))
    mask = view_time_matrix == 0
    sns.heatmap(view_time_matrix, mask = mask ,annot=True, cmap="YlGnBu", cbar_kws={'label': 'Median der Betrachtungsdauer in Sekunden'})
    plt.title("Matrix Betrachtungsdauer")
    plt.xlabel("Präsenz von Text")
    plt.ylabel("Kategorien")
    plt.show()

def plot_split_cell_matrix(data):
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    from matplotlib.patches import Polygon

    print("SPLIT CELL MATRIX")
    cop = data.copy()
    cop = cop.groupby('categoryCode').agg({'duration': 'median'}).reset_index()
    
    # Kategorien, Ursprung unten links -> Reihenfolge NICHT invertieren
    semantic_categories = ["meme", "ort", "person", "politik"]
    print(semantic_categories)
    df = pd.DataFrame(0, index=semantic_categories, columns=semantic_categories, dtype=float)
    
    # Jede Zelle speichert [ohneText, mitText]
    df = df.map(lambda x: [-1, -1])

    for idx, row in cop.iterrows():
        if row["categoryCode"] == "00001":
            continue
        else:
            cur_categories = get_categories(row['categoryCode'])
            if str(int(row["categoryCode"])).endswith("1"):
                # Text
                cur_categories.remove("text")
                print("cur_categories:", cur_categories)
                if len(cur_categories) == 1:
                    df.at[cur_categories[0], cur_categories[0]][1] = row["duration"]
                elif len(cur_categories) == 2:
                    df.at[cur_categories[0], cur_categories[1]][1] = row["duration"]
                    df.at[cur_categories[1], cur_categories[0]][1] = row["duration"]
                else:
                    print("Skipping multi-category:", cur_categories)
            else:
                # Kein Text
                if len(cur_categories) == 1:
                    df.at[cur_categories[0], cur_categories[0]][0] = row["duration"]
                elif len(cur_categories) == 2:
                    df.at[cur_categories[0], cur_categories[1]][0] = row["duration"]
                    df.at[cur_categories[1], cur_categories[0]][0] = row["duration"]

    # Normalisierung für Farbskala
    all_vals = np.array([v for row in df.values for v in row])
    vals1 = all_vals[:,0]
    vals2 = all_vals[:,1]
    vmin = min(vals1.min(), vals2.min())
    vmax = max(vals1.max(), vals2.max())
    cmap = plt.cm.viridis

    fig, ax = plt.subplots(figsize=(6,6))

    n = len(df)
    for i, row in enumerate(df.index):
        for j, col in enumerate(df.columns):
            val1, val2 = df.loc[row, col]

            # Mapping: Ursprung unten links
            x0, y0 = j, i
            x1, y1 = j+1, i+1

            # Teilung von unten links nach oben rechts
            tri1 = [(x0,y0),(x1,y0),(x1,y1)]  # unten-rechts -> ohne Text
            tri2 = [(x0,y0),(x0,y1),(x1,y1)]  # oben-links -> mit Text

            color1 = cmap((val1-vmin)/(vmax-vmin)) if vmax>vmin else (1,1,1,1)
            color2 = cmap((val2-vmin)/(vmax-vmin)) if vmax>vmin else (1,1,1,1)
            
            ax.add_patch(Polygon(tri1, facecolor=color1))
            ax.add_patch(Polygon(tri2, facecolor=color2))
            
            if val1!=0 or val2!=0:
                ax.text(j+0.7, i+0.3, f"{val1:.1f}", ha="center", va="center", fontsize=7)
                ax.text(j+0.3, i+0.7, f"{val2:.1f}", ha="center", va="center", fontsize=7)

    # Achsen
    ax.set_xticks(np.arange(n)+0.5)
    ax.set_yticks(np.arange(n)+0.5)
    ax.set_xticklabels(df.columns)
    ax.set_yticklabels(df.index)

    ax.set_xlim(0,n)
    ax.set_ylim(0,n)
    ax.set_aspect("equal")

    # Farbskala
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Tuple values")

    plt.show()


def plot_tag_groups(data):
    
    df = data.copy()
    df = df.groupby('categoryCode').agg({'duration': 'median'}).reset_index()
    
    df["categoryCode"] = df["categoryCode"].astype(str).str.zfill(5)
    
    for e in df.index:
        
        for i in range(5):
            print(df["categoryCode"].iloc[e][i])
            if df["categoryCode"].iloc[e][i] == '1':
                
                tmp = df["categoryCode"].iloc[e]
                df["categoryCode"].iloc[e] = tmp + "_" + categories[i]
    # sort by duration
    df = df.sort_values(by='duration', ascending=False)

    print("TAG ANALYSIS ",df)
    
    plt.figure(figsize=(12, 8))
    plt.barh(range(len(df)), df['duration'])
    plt.yticks(range(len(df)), df['categoryCode'])
    plt.xlabel('Median System Time Diff (seconds)')
    plt.title('Median Viewing Time by Tag Group')
    plt.tight_layout()
    plt.show()

def get_median_for_image(data, image_id):
    df = data.copy()
    image_data = df[df['imageID'] == int(image_id)]
    if not image_data.empty:
        return image_data['duration'].median()
    else:
        print("2")
        return None
    
def detect_anomalies():
    data = pd.read_csv("EWS/code/analysis/duration/eyetracking_summary.csv")
    anomalies = data[(data['duration'] <= 5) | (data['duration'] > 16)]
    print("\n" + "="*80)
    print("ANOMALIES DETECTION")
    print("="*80)
    if anomalies.empty:
        print("No anomalies detected.")
    else:
        print(f"Total anomalies detected: {len(anomalies)}")
        print(anomalies)

def censored_regression(data,fitter):

    df = data.copy()

    # 1. Define censoring
    df["event_observed"] = ~df["duration"].isin([5.0, 15.0])  

    # 2. Split categoryCode into individual binary columns
    # Ensure it's a 5-character string
    df["categoryCode"] = df["categoryCode"].astype(str).str.zfill(5)
    
    for i in range(5):  # five digits
        df[categories[i]] = df["categoryCode"].str[i].astype(int)

    # 3. Fit Weibull AFT model
    aft_dict = {
        "Weibull": WeibullAFTFitter,
        "LogNormal": LogNormalAFTFitter,
        "CoxPH": CoxPHFitter,
        "KaplanMeier": KaplanMeierFitter,
        "LogLogistic": LogLogisticAFTFitter
    }
    aft = aft_dict[fitter]()
    aft.fit(
        df,
        duration_col="duration",
        event_col="event_observed",
        formula="meme + ort + person + politik + text + words"
    )

    # 4. Show results
    aft.print_summary()
    aft.plot()


#plot_tag_groups(pd.read_csv("EWS/code/analysis/duration/view_durations.csv"))
#plot_view_time_matrix(pd.read_csv("EWS/code/analysis/duration/view_durations.csv"))
#plot_split_cell_matrix(pd.read_csv("EWS/code/analysis/duration/view_durations.csv"))
censored_regression(pd.read_csv("EWS/code/analysis/duration/view_durations.csv"), "LogNormal")

#myframe = create_normalized_df(data = pd.read_csv("EWS/code/analysis/duration/view_durations.csv"))
#plot_tag_groups(myframe)
