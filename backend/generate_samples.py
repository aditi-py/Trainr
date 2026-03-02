"""Generate 15 sample datasets (3 per file type) for HappyModel demo."""
import pandas as pd
import numpy as np
import json
import os

np.random.seed(42)
OUT = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(OUT, exist_ok=True)

# ── CSV 1: house_prices ───────────────────────────────────────────────────────
n = 200
sqft       = np.random.randint(600, 4500, n)
bedrooms   = np.random.randint(1, 6, n)
bathrooms  = np.random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4], n)
garage     = np.random.randint(0, 4, n)
location   = np.random.choice(["Urban","Suburban","Rural"], n)
age        = np.random.randint(0, 80, n)
loc_bonus  = np.where(location=="Urban", 50000, np.where(location=="Suburban", 20000, 0))
price      = (sqft*120 + bedrooms*8000 + bathrooms*5000 + garage*4000
              - age*500 + loc_bonus + np.random.normal(0, 10000, n)).astype(int)
price      = np.clip(price, 80000, 900000)
pd.DataFrame({"sqft":sqft,"bedrooms":bedrooms,"bathrooms":bathrooms,"garage":garage,
               "location":location,"age_years":age,"price":price})\
  .to_csv(f"{OUT}/house_prices.csv", index=False)
print("house_prices.csv")

# ── CSV 2: customer_churn ─────────────────────────────────────────────────────
n = 250
tenure   = np.random.randint(0, 72, n)
monthly  = np.round(np.random.uniform(20, 120, n), 2)
contract = np.random.choice(["Month-to-month","One year","Two year"], n)
tech_sup = np.random.choice(["Yes","No"], n)
online_s = np.random.choice(["Yes","No"], n)
crisk    = np.where(contract=="Month-to-month", 0.4, np.where(contract=="One year", 0.15, 0.05))
churn_p  = np.clip(crisk + (monthly/120)*0.3 - (tenure/72)*0.25 + np.random.normal(0, 0.1, n), 0, 1)
churned  = (churn_p > 0.4).astype(int)
pd.DataFrame({"tenure_months":tenure,"monthly_charges":monthly,"contract_type":contract,
               "tech_support":tech_sup,"online_security":online_s,"churned":churned})\
  .to_csv(f"{OUT}/customer_churn.csv", index=False)
print("customer_churn.csv")

# ── CSV 3: diabetes_risk ──────────────────────────────────────────────────────
n = 220
age2     = np.random.randint(20, 80, n)
bmi      = np.round(np.random.uniform(18, 45, n), 1)
glucose  = np.random.randint(70, 200, n)
bp       = np.random.randint(60, 140, n)
insulin  = np.random.randint(0, 300, n)
fam_hx   = np.random.choice(["Yes","No"], n)
rscore   = (glucose/200*0.4 + bmi/45*0.3 + age2/80*0.2
            + (fam_hx=="Yes").astype(int)*0.1 + np.random.normal(0, 0.05, n))
at_risk  = (rscore > 0.45).astype(int)
pd.DataFrame({"age":age2,"bmi":bmi,"glucose":glucose,"blood_pressure":bp,
               "insulin":insulin,"family_history":fam_hx,"at_risk":at_risk})\
  .to_csv(f"{OUT}/diabetes_risk.csv", index=False)
print("diabetes_risk.csv")

# ── EXCEL 1: retail_sales ─────────────────────────────────────────────────────
n = 200
region    = np.random.choice(["North","South","East","West"], n)
category  = np.random.choice(["Electronics","Clothing","Food","Sports"], n)
promo     = np.random.randint(0, 5, n)
traffic   = np.random.randint(100, 2000, n)
week      = np.random.randint(1, 53, n)
rmult     = np.where(region=="North", 1.2, np.where(region=="South", 0.9, 1.0))
sales     = np.clip(((traffic*12 + promo*800 + np.random.normal(0, 500, n))*rmult).astype(int), 500, 50000)
pd.DataFrame({"region":region,"category":category,"promotions":promo,
               "foot_traffic":traffic,"week_of_year":week,"weekly_sales":sales})\
  .to_excel(f"{OUT}/retail_sales.xlsx", index=False)
print("retail_sales.xlsx")

# ── EXCEL 2: student_performance ──────────────────────────────────────────────
n = 200
study    = np.round(np.random.uniform(0, 12, n), 1)
attend   = np.round(np.random.uniform(40, 100, n), 1)
assign   = np.random.randint(0, 20, n)
prev_gpa = np.round(np.random.uniform(1.5, 4.0, n), 2)
parental = np.random.choice(["Low","Medium","High"], n)
par_b    = np.where(parental=="High", 8, np.where(parental=="Medium", 4, 0))
grade    = np.clip(np.round(study*2.5 + attend*0.25 + assign*0.8 + prev_gpa*10 + par_b
                             + np.random.normal(0, 5, n), 1), 0, 100)
pd.DataFrame({"study_hours":study,"attendance_pct":attend,"assignments_done":assign,
               "prev_gpa":prev_gpa,"parental_support":parental,"final_grade":grade})\
  .to_excel(f"{OUT}/student_performance.xlsx", index=False)
print("student_performance.xlsx")

# ── EXCEL 3: loan_approval ────────────────────────────────────────────────────
n = 220
income   = np.random.randint(20000, 200000, n)
loan_amt = np.random.randint(5000, 500000, n)
credit   = np.random.randint(300, 850, n)
emp_yrs  = np.random.randint(0, 30, n)
debt_r   = np.round(np.random.uniform(0.05, 0.8, n), 2)
prop_v   = np.random.randint(50000, 800000, n)
score    = np.clip(credit/850*0.45 + income/200000*0.25 - debt_r*0.2
                   + emp_yrs/30*0.1 + np.random.normal(0, 0.05, n), 0, 1)
approved = (score > 0.45).astype(int)
pd.DataFrame({"income":income,"loan_amount":loan_amt,"credit_score":credit,
               "employment_years":emp_yrs,"debt_ratio":debt_r,
               "property_value":prop_v,"approved":approved})\
  .to_excel(f"{OUT}/loan_approval.xlsx", index=False)
print("loan_approval.xlsx")

# ── PARQUET 1: energy_consumption ─────────────────────────────────────────────
n = 300
hour     = np.random.randint(0, 24, n)
temp     = np.round(np.random.uniform(-5, 40, n), 1)
humidity = np.random.randint(20, 95, n)
day_type = np.random.choice(["Weekday","Weekend"], n)
occupancy= np.random.randint(0, 100, n)
is_peak  = ((hour >= 8) & (hour <= 20)).astype(int)
energy   = np.clip(np.round(occupancy*0.4 + abs(temp-20)*0.3 + is_peak*5
                             + humidity*0.05 + np.random.normal(0, 2, n), 2), 1, 80)
pd.DataFrame({"hour":hour,"temperature_c":temp,"humidity_pct":humidity,
               "day_type":day_type,"occupancy_pct":occupancy,"energy_kwh":energy})\
  .to_parquet(f"{OUT}/energy_consumption.parquet", index=False)
print("energy_consumption.parquet")

# ── PARQUET 2: fraud_detection ────────────────────────────────────────────────
n = 300
amount   = np.round(np.random.exponential(80, n) + 5, 2)
merch    = np.random.choice(["Retail","Online","Travel","Food","ATM"], n)
dist_hm  = np.round(np.random.exponential(20, n), 1)
online   = np.random.randint(0, 2, n)
chip     = np.random.randint(0, 2, n)
mcat_r   = np.where(merch=="Online", 0.3, np.where(merch=="ATM", 0.25, 0.05))
fraud_p  = np.clip(mcat_r + (amount/500)*0.2 + online*0.15 - chip*0.1
                   + dist_hm/200*0.1 + np.random.normal(0, 0.05, n), 0, 1)
is_fraud = (fraud_p > 0.4).astype(int)
pd.DataFrame({"amount":amount,"merchant_category":merch,"distance_from_home_km":dist_hm,
               "online_order":online,"used_chip":chip,"is_fraud":is_fraud})\
  .to_parquet(f"{OUT}/fraud_detection.parquet", index=False)
print("fraud_detection.parquet")

# ── PARQUET 3: traffic_flow ───────────────────────────────────────────────────
n = 280
hour2    = np.random.randint(0, 24, n)
weather  = np.random.choice(["Clear","Rain","Fog","Snow"], n)
day_t    = np.random.choice(["Weekday","Weekend","Holiday"], n)
spd_lim  = np.random.choice([30,40,50,60,80,100], n)
incidents= np.random.randint(0, 5, n)
rush     = (((hour2>=7)&(hour2<=9))|((hour2>=16)&(hour2<=19))).astype(int)
w_pen    = np.where(weather=="Clear", 0, np.where(weather=="Rain", 15, np.where(weather=="Snow", 40, 25)))
veh      = np.clip((rush*500 + spd_lim*8 - incidents*30 - w_pen*5
                    + np.random.normal(0, 50, n)).astype(int), 0, 2000)
pd.DataFrame({"hour":hour2,"weather":weather,"day_type":day_t,
               "speed_limit_kmh":spd_lim,"incidents":incidents,"vehicle_count":veh})\
  .to_parquet(f"{OUT}/traffic_flow.parquet", index=False)
print("traffic_flow.parquet")

# ── JSON 1: user_engagement ───────────────────────────────────────────────────
n = 220
age3    = np.random.randint(18, 70, n)
pages   = np.random.randint(1, 40, n)
device  = np.random.choice(["Mobile","Desktop","Tablet"], n)
tod     = np.random.choice(["Morning","Afternoon","Evening","Night"], n)
new_usr = np.random.randint(0, 2, n)
referral= np.random.choice(["Organic","Social","Email","Paid"], n)
dev_b   = np.where(device=="Desktop", 60, np.where(device=="Tablet", 40, 20))
session = np.clip((pages*30 + dev_b - new_usr*30 + np.random.normal(0, 40, n)).astype(int), 10, 1800)
records = [{"age":int(age3[i]),"pages_viewed":int(pages[i]),"device_type":device[i],
            "time_of_day":tod[i],"new_user":int(new_usr[i]),
            "referral_source":referral[i],"session_duration_sec":int(session[i])} for i in range(n)]
with open(f"{OUT}/user_engagement.json", "w") as f:
    json.dump(records, f)
print("user_engagement.json")

# ── JSON 2: medical_diagnosis ─────────────────────────────────────────────────
n = 200
age4  = np.random.randint(20, 80, n)
sbp   = np.random.randint(90, 200, n)
dbp   = np.random.randint(50, 120, n)
bmi2  = np.round(np.random.uniform(16, 45, n), 1)
chol  = np.random.randint(120, 320, n)
smoke = np.random.choice(["Never","Former","Current"], n)
smk_r = np.where(smoke=="Current", 0.25, np.where(smoke=="Former", 0.1, 0))
risk2 = (sbp/200*0.3 + bmi2/45*0.25 + chol/320*0.2 + age4/80*0.15
         + smk_r + np.random.normal(0, 0.05, n))
diag  = np.where(risk2 > 0.45, "High Risk", np.where(risk2 > 0.3, "Moderate Risk", "Low Risk"))
records = [{"age":int(age4[i]),"systolic_bp":int(sbp[i]),"diastolic_bp":int(dbp[i]),
            "bmi":float(bmi2[i]),"cholesterol":int(chol[i]),
            "smoking_status":smoke[i],"diagnosis":diag[i]} for i in range(n)]
with open(f"{OUT}/medical_diagnosis.json", "w") as f:
    json.dump(records, f)
print("medical_diagnosis.json")

# ── JSON 3: wine_quality ──────────────────────────────────────────────────────
n = 250
alc   = np.round(np.random.uniform(8, 15, n), 1)
vacid = np.round(np.random.uniform(0.1, 1.2, n), 2)
sulph = np.round(np.random.uniform(0.3, 2.0, n), 2)
cit   = np.round(np.random.uniform(0, 1, n), 2)
res_s = np.round(np.random.uniform(1, 15, n), 1)
ph    = np.round(np.random.uniform(2.8, 4.0, n), 2)
qual  = np.clip(np.round(alc*0.4 - vacid*1.5 + sulph*0.8 + cit*0.5
                          - abs(ph-3.5)*0.5 + np.random.normal(0, 0.5, n) + 4.5).astype(int), 1, 10)
records = [{"alcohol":float(alc[i]),"volatile_acidity":float(vacid[i]),
            "sulphates":float(sulph[i]),"citric_acid":float(cit[i]),
            "residual_sugar":float(res_s[i]),"ph":float(ph[i]),
            "quality":int(qual[i])} for i in range(n)]
with open(f"{OUT}/wine_quality.json", "w") as f:
    json.dump(records, f)
print("wine_quality.json")

# ── TXT 1: air_quality ────────────────────────────────────────────────────────
n = 220
pm25  = np.round(np.random.exponential(25, n) + 5, 1)
pm10  = np.round(pm25 * np.random.uniform(1.5, 2.5, n), 1)
no2   = np.round(np.random.uniform(5, 120, n), 1)
co    = np.round(np.random.uniform(0.1, 5.0, n), 2)
tmp   = np.round(np.random.uniform(-5, 40, n), 1)
hum   = np.random.randint(20, 95, n)
wind  = np.round(np.random.uniform(0, 25, n), 1)
aqi   = np.clip((pm25*1.2 + pm10*0.5 + no2*0.3 + co*5 - wind*2
                 + np.random.normal(0, 5, n)).astype(int), 0, 500)
pd.DataFrame({"pm25":pm25,"pm10":pm10,"no2":no2,"co":co,
               "temperature_c":tmp,"humidity_pct":hum,"wind_speed_mps":wind,"aqi":aqi})\
  .to_csv(f"{OUT}/air_quality.txt", index=False, sep="\t")
print("air_quality.txt")

# ── TXT 2: delivery_time ──────────────────────────────────────────────────────
n = 200
dist  = np.round(np.random.uniform(1, 500, n), 1)
wt    = np.round(np.random.uniform(0.1, 50, n), 2)
prio  = np.random.choice(["Standard","Express","Same-Day"], n)
frag  = np.random.randint(0, 2, n)
carr  = np.random.choice(["DHL","FedEx","UPS","Local"], n)
seas  = np.random.choice(["Spring","Summer","Autumn","Winter"], n)
pmult = np.where(prio=="Same-Day", 0.3, np.where(prio=="Express", 0.6, 1.0))
smult = np.where(seas=="Winter", 1.3, 1.0)
days  = np.clip(np.round((dist/200*5 + wt/50*2 + frag*0.5
                           + np.random.normal(0, 0.5, n)) * pmult * smult, 1), 0.1, 15.0)
pd.DataFrame({"distance_km":dist,"weight_kg":wt,"priority_level":prio,
               "fragile":frag,"carrier":carr,"season":seas,"delivery_days":days})\
  .to_csv(f"{OUT}/delivery_time.txt", index=False, sep="\t")
print("delivery_time.txt")

# ── TXT 3: crop_yield ────────────────────────────────────────────────────────
n = 220
rain  = np.round(np.random.uniform(200, 1500, n), 1)
tmp2  = np.round(np.random.uniform(10, 40, n), 1)
soil  = np.round(np.random.uniform(4.5, 8.5, n), 1)
fert  = np.round(np.random.uniform(0, 200, n), 1)
pest  = np.round(np.random.uniform(0, 100, n), 1)
area  = np.round(np.random.uniform(0.5, 50, n), 2)
crop  = np.random.choice(["Wheat","Rice","Maize","Soybean"], n)
yld   = np.clip(np.round(rain/1500*3 + fert/200*2.5 - abs(tmp2-25)/30*1.5
                           + pest/100*0.5 + np.random.normal(0, 0.3, n), 2), 0.5, 8.0)
pd.DataFrame({"rainfall_mm":rain,"temperature_c":tmp2,"soil_ph":soil,
               "fertilizer_kg_ha":fert,"pesticide_ml_ha":pest,
               "area_hectares":area,"crop_type":crop,"yield_tons_ha":yld})\
  .to_csv(f"{OUT}/crop_yield.txt", index=False, sep="\t")
print("crop_yield.txt")

print(f"\nDone — 15 sample datasets in {OUT}")
