# CÔNG THỨC TÍNH TOÁN SPORT_BETTING_MODULE

## Mục Lục
1. [Công Thức Risk Management](#công-thức-risk-management)
2. [Công Thức Cược Cơ Bản](#công-thức-cược-cơ-bản)
3. [Công Thức Cược Nâng Cao](#công-thức-cược-nâng-cao)
4. [Công Thức Cược Hệ](#công-thức-cược-hệ)
5. [Công Thức Live Betting](#công-thức-live-betting)
6. [Công Thức Thống Kê](#công-thức-thống-kê)
7. [Công Thức Machine Learning](#công-thức-machine-learning)
8. [Công Thức Tài Chính](#công-thức-tài-chính)
9. [Công Thức P2P Marketplace](#công-thức-p2p-marketplace)

---

## Công Thức Risk Management

### Công Thức Tính Trách Nhiệm Ròng
```
Trách nhiệm RÒNG nếu "Kết quả X" xảy ra = 
(Tổng Payout nếu X xảy ra bao gồm cả PROMOTION) - 
(Tổng Tiền Cược vào TẤT CẢ CÁC KẾT QUẢ CÒN LẠI)
```

### Công Thức Tính Tỷ Lệ Cược Chào Bán (Risk-Adjusted Offered Odds)
```
Odds_chào_bán = (Odds_lý_thuyết / M) * (1 - (L_ròng / T_cố_định))
```
Trong đó:
- M: Biên lợi nhuận mong muốn (ví dụ: 1.05)
- L_ròng: Trách nhiệm ròng hiện tại
- T_cố_định: Trần cố định rủi ro

### Công Thức Tính Biên Lợi Nhuận
```
Biên lợi nhuận = Tổng xác suất nghịch đảo - 100%
Ví dụ: (1/1.90) + (1/1.90) = 52.63% + 52.63% = 105.26%
Biên lợi nhuận = 5.26%
```

### Công Thức Dynamic Odds
```
Odds_mới = Odds_cũ × (1 - (Rủi_ro_hiện_tại / Ngưỡng_rủi_ro))
```

---

## Công Thức Cược Cơ Bản

### Công Thức Tính Payout
```
Payout = Stake × Odds
Lợi nhuận = Payout - Stake
```

### Công Thức Cược Kép (Accumulator)
```
Tỷ lệ tổng = Odds1 × Odds2 × ... × OddsN
Payout = Stake × Tỷ lệ tổng
```

### Công Thức Handicap
```
Kết quả cuối = Kết quả thực + Handicap
Nếu Kết quả cuối > 0: Đội chấp thắng
Nếu Kết quả cuối < 0: Đội được chấp thắng
Nếu Kết quả cuối = 0: Hòa (hoàn tiền)
```

### Công Thức Asian Handicap
```
Kết quả cuối = Kết quả thực + Handicap
Nếu Kết quả cuối > 0.5: Đội chấp thắng
Nếu Kết quả cuối < 0.5: Đội được chấp thắng
Nếu Kết quả cuối = 0.5: Hòa (hoàn tiền)
```

### Công Thức Over/Under
```
Tổng bàn thắng > Over: Thắng cược Over
Tổng bàn thắng < Under: Thắng cược Under
Tổng bàn thắng = Over/Under: Hòa (hoàn tiền)
```

---

## Công Thức Cược Nâng Cao

### Công Thức Both Teams to Score (BTTS)
```
P(BTTS) = P(Home_Score > 0) × P(Away_Score > 0)
P(BTTS_No) = 1 - P(BTTS)
```

### Công Thức Correct Score
```
P(Score = x-y) = P(Home_Score = x) × P(Away_Score = y)
```

### Công Thức Half Time/Full Time
```
P(HT/FT) = P(HT_Result) × P(FT_Result | HT_Result)
```

### Công Thức 1X2
```
P(1) = P(Home_Win)
P(X) = P(Draw)
P(2) = P(Away_Win)
P(1) + P(X) + P(2) = 1
```

---

## Công Thức Cược Hệ

### Cược Hệ 2/3
```
- 3 cược đơn: A, B, C
- 3 cược đôi: AB, AC, BC
- Tổng cược = 6 cược
```

### Cược Hệ 3/4
```
- 4 cược đơn: A, B, C, D
- 6 cược đôi: AB, AC, AD, BC, BD, CD
- 4 cược ba: ABC, ABD, ACD, BCD
- Tổng cược = 14 cược
```

### Lucky 15 (4 selections)
```
- 4 cược đơn
- 6 cược đôi
- 4 cược ba
- 1 cược bốn
- Tổng cược = 15 cược
```

### Lucky 31 (5 selections)
```
- 5 cược đơn
- 10 cược đôi
- 10 cược ba
- 5 cược bốn
- 1 cược năm
- Tổng cược = 31 cược
```

### Trixie (3 selections)
```
- 3 cược đôi
- 1 cược ba
- Tổng cược = 4 cược
```

### Yankee (4 selections)
```
- 6 cược đôi
- 4 cược ba
- 1 cược bốn
- Tổng cược = 11 cược
```

### Patent (3 selections)
```
- 3 cược đơn
- 3 cược đôi
- 1 cược ba
- Tổng cược = 7 cược
```

### Canadian (5 selections)
```
- 10 cược đôi
- 10 cược ba
- 5 cược bốn
- 1 cược năm
- Tổng cược = 26 cược
```

### Heinz (6 selections)
```
- 15 cược đôi
- 20 cược ba
- 15 cược bốn
- 6 cược năm
- 1 cược sáu
- Tổng cược = 57 cược
```

### Super Heinz (7 selections)
```
- 21 cược đôi
- 35 cược ba
- 35 cược bốn
- 21 cược năm
- 7 cược sáu
- 1 cược bảy
- Tổng cược = 120 cược
```

### Goliath (8 selections)
```
- 28 cược đôi
- 56 cược ba
- 70 cược bốn
- 56 cược năm
- 28 cược sáu
- 8 cược bảy
- 1 cược tám
- Tổng cược = 247 cược
```

---

## Công Thức Live Betting

### Công Thức Next Goal
```
P(Next_Goal_Home) = λ_home / (λ_home + λ_away)
P(Next_Goal_Away) = λ_away / (λ_home + λ_away)
```
Trong đó:
- λ_home, λ_away: Tỷ lệ ghi bàn của đội nhà và đội khách

### Công Thức Time of Next Goal
```
P(Goal_in_t) = λ × e^(-λt)
```
Trong đó:
- λ: Tỷ lệ ghi bàn trung bình
- t: Thời gian (phút)

### Công Thức Total Goals Live
```
P(Total_Goals = n) = (λ^t)^n × e^(-λt) / n!
```

---

## Công Thức Thống Kê

### Công Thức Tính Xác Suất Thắng
```
P(Thắng) = 1 / Odds
P(Thua) = 1 - P(Thắng)
```

### Công Thức Tính Implied Probability
```
Implied_Probability = 1 / Odds × 100%
```

### Công Thức Tính True Probability
```
True_Probability = Implied_Probability / (1 + Margin)
```

### Công Thức Tính Margin (Biên Lợi Nhuận)
```
Margin = (1/Odds_1 + 1/Odds_2 + ... + 1/Odds_n) - 1
```

### Công Thức Tính Value Bet
```
Value = (True_Probability × Odds) - 1
Nếu Value > 0: Cược có giá trị
Nếu Value ≤ 0: Cược không có giá trị
```

### Công Thức Tính ROI (Return on Investment)
```
ROI = (Tổng_Lợi_Nhuận / Tổng_Vốn_Đầu_Tư) × 100%
```

### Công Thức Tính Sharpe Ratio
```
Sharpe_Ratio = (ROI - Risk_Free_Rate) / Standard_Deviation
```

### Công Thức Tính Standard Deviation
```
σ = √(Σ(xi - μ)² / N)
```

### Công Thức Tính Correlation
```
r = Σ((xi - x̄)(yi - ȳ)) / √(Σ(xi - x̄)² × Σ(yi - ȳ)²)
```

### Công Thức Tính Regression
```
y = mx + b
m = Σ((xi - x̄)(yi - ȳ)) / Σ(xi - x̄)²
b = ȳ - m×x̄
```

---

## Công Thức Machine Learning

### Công Thức Logistic Regression
```
P(Y=1) = 1 / (1 + e^(-(β₀ + β₁X₁ + ... + βₙXₙ)))
```

### Công Thức Linear Regression
```
y = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ + ε
```

### Công Thức Gradient Descent
```
θ_new = θ_old - α × ∇J(θ)
```

### Công Thức Mean Squared Error
```
MSE = (1/n) × Σ(yi - ŷi)²
```

### Công Thức Cross-Entropy Loss
```
CE = -Σ(yi × log(ŷi) + (1-yi) × log(1-ŷi))
```

### Mô Hình Poisson cho Bóng Đá
```
P(k;λ) = (e^-λ * λ^k) / k!
```
Trong đó:
- k: Số bàn thắng
- λ: Số bàn thắng kỳ vọng (Expected Goals)
- e: Hằng số Euler (≈ 2.718)

### Mô Hình Elo Rating cho Dự Đoán Kết Quả
```
P(A thắng) = 1 / (1 + 10^((R_B - R_A) / 400))
P(B thắng) = 1 / (1 + 10^((R_A - R_B) / 400))
```
Trong đó:
- R_A, R_B: Điểm Elo của đội A và B
- 400: Hệ số K (độ nhạy của rating)

### Công Thức Cập Nhật Elo Rating
```
R_new = R_old + K × (S - E)
```
Trong đó:
- S: Kết quả thực tế (1 = thắng, 0.5 = hòa, 0 = thua)
- E: Xác suất thắng dự đoán
- K: Hệ số K (thường = 32)

### Mô Hình Bradley-Terry cho So Sánh Đội Bóng
```
P(i thắng j) = π_i / (π_i + π_j)
```
Trong đó:
- π_i, π_j: Tham số sức mạnh của đội i và j

### Công Thức Kelly Criterion cho Quản Lý Tiền Cược
```
f* = (bp - q) / b
```
Trong đó:
- f*: Tỷ lệ tiền cược tối ưu
- b: Tỷ lệ cược (odds - 1)
- p: Xác suất thắng
- q: Xác suất thua (1 - p)

### Công Thức Tính Expected Value (EV)
```
EV = (P_win × Payout) - (P_lose × Stake)
EV = (P_win × (Odds × Stake)) - (P_lose × Stake)
```

---

## Công Thức Tài Chính

### Công Thức Tính Lãi Suất Kép
```
A = P(1 + r/n)^(nt)
```

### Công Thức Tính Present Value
```
PV = FV / (1 + r)^t
```

### Công Thức Tính Future Value
```
FV = PV × (1 + r)^t
```

### Công Thức Tính Net Present Value
```
NPV = Σ(CFt / (1 + r)^t) - Initial_Investment
```

### Công Thức Tính Internal Rate of Return
```
NPV = 0 = Σ(CFt / (1 + IRR)^t) - Initial_Investment
```

### Công Thức Tính Payback Period
```
Payback_Period = Initial_Investment / Annual_Cash_Flow
```

### Công Thức Tính Profitability Index
```
PI = NPV / Initial_Investment
```

### Công Thức Tính Số Dư Ví
```
Số dư khả dụng = Tổng nạp - Tổng rút - Tiền đang cược - Tiền đóng băng
Số dư tổng = Số dư khả dụng + Tiền đóng băng
```

---

## Công Thức P2P Marketplace

### Công Thức Tính Giá Trị Công Bằng
```
Giá trị Công bằng = Tiền cược gốc × Tỷ lệ cược gốc / Tỷ lệ cược trực tiếp
```

### Công Thức Tính Giá Trị Cash Out
```
Giá trị Cash Out = Giá trị Công Bằng × (1 − Phí Cash Out)
```

### Công Thức Phân Chia Lợi Nhuận
```
Lợi nhuận người sở hữu = Tổng lợi nhuận × (Phần sở hữu / 100%)
```

---

## Công Thức Saga Pattern

### Luồng Đặt Cược
```
1. Betting Service: Tạo cược PENDING → Phát BetPlaced
2. Wallet Service: Lắng nghe BetPlaced → Trừ tiền
   - Thành công → Phát FundsDebited
   - Thất bại → Phát DebitFailed
3. Betting Service: 
   - Lắng nghe FundsDebited → Cập nhật CONFIRMED
   - Lắng nghe DebitFailed → Cập nhật CANCELLED
```

### Luồng Cash Out
```
1. Betting Service: Phát CashoutRequested → Cập nhật CASHING_OUT
2. Wallet Service: Lắng nghe CashoutRequested → Cộng tiền
   - Thành công → Phát CashoutFundsCredited
   - Thất bại → Phát CashoutFailed
3. Betting Service:
   - Lắng nghe CashoutFundsCredited → Cập nhật CASHED_OUT
   - Lắng nghe CashoutFailed → Chuyển về ACTIVE
4. Risk Management: Lắng nghe CashoutFundsCredited → Xóa trách nhiệm
```

---

## Công Thức Carousel Service

### Công Thức Ưu Tiên Hiển Thị
```
Ưu tiên = (Trạng thái == "chưa_mua") ? 1 : 0
Thứ tự = Ưu tiên DESC, RANDOM()
```

### Công Thức Auto-Play
```
Thời gian hiển thị = 5 giây/sản phẩm
Tổng thời gian = Số sản phẩm × 5 giây
```

### Công Thức Tối Ưu Thiết Bị
```
Desktop/Tablet: 4.5 sản phẩm/lần, tổng 20 sản phẩm
Mobile: 2.5 sản phẩm/lần, tổng 15 sản phẩm
```

---

## Công Thức Cờ Bạc Truyền Thống

### Công Thức Xác Suất Xúc Xắc
```
P(Tổng = n) = Số cách có thể / 36
P(Tổng = 7) = 6/36 = 1/6 ≈ 16.67%
P(Tổng = 2) = 1/36 ≈ 2.78%
P(Tổng = 12) = 1/36 ≈ 2.78%
```

### Công Thức Xác Suất Bài Tây
```
P(Rút được Át) = 4/52 = 1/13 ≈ 7.69%
P(Rút được 2 quân cùng chất) = C(13,2) / C(52,2) = 78/1326 ≈ 5.88%
P(Flush) = C(13,5) × 4 / C(52,5) ≈ 0.198%
P(Straight) = 10 × 4^5 / C(52,5) ≈ 0.392%
```

### Công Thức Blackjack
```
P(Blackjack) = P(Át) × P(10) × 2 = (4/52) × (16/51) × 2 ≈ 4.83%
P(Bust) = P(Tổng > 21)
P(21) = P(Tổng = 21)
```

### Công Thức Roulette
```
P(Đỏ) = 18/37 ≈ 48.65% (European)
P(Đỏ) = 18/38 ≈ 47.37% (American)
P(Số đơn) = 1/37 ≈ 2.70% (European)
P(Số đơn) = 1/38 ≈ 2.63% (American)
```

### Công Thức Baccarat
```
P(Banker thắng) ≈ 45.86%
P(Player thắng) ≈ 44.62%
P(Tie) ≈ 9.52%
```

---

## Công Thức Cá Cược Thể Thao Nâng Cao

### Công Thức Asian Handicap Chi Tiết
```
Kết quả cuối = Kết quả thực + Handicap
Nếu Kết quả cuối > 0.5: Đội chấp thắng
Nếu Kết quả cuối < 0.5: Đội được chấp thắng
Nếu Kết quả cuối = 0.5: Hòa (hoàn tiền)

Handicap 0.5: Không có hòa
Handicap 1.0: Có thể hòa
Handicap 1.5: Không có hòa
```

### Công Thức First Goal Scorer
```
P(Player A ghi bàn đầu) = P(A ghi bàn) × P(Không ai khác ghi bàn trước A)
P(A ghi bàn) = λ_A / (λ_A + λ_B + λ_C + ...)
```

### Công Thức Anytime Goalscorer
```
P(Player A ghi bàn bất kỳ) = 1 - e^(-λ_A × t)
Trong đó: t = thời gian trận đấu (phút)
```

### Công Thức Clean Sheet
```
P(Clean Sheet) = e^(-λ_opponent × t)
P(Concede) = 1 - P(Clean Sheet)
```

### Công Thức Corners
```
P(Corners > n) = 1 - Σ(k=0 to n) (λ^t)^k × e^(-λ^t) / k!
```

### Công Thức Cards
```
P(Cards > n) = 1 - Σ(k=0 to n) (λ^t)^k × e^(-λ^t) / k!
```

---

## Công Thức In-Play Betting

### Công Thức Time Decay
```
P(Event trong t phút) = P(Event) × e^(-λ × t)
```

### Công Thức Momentum
```
Momentum = (Recent_Goals - Expected_Goals) / Time_Remaining
```

### Công Thức Pressure Index
```
Pressure = (Home_Score - Away_Score) / Time_Remaining
```

### Công Thức Form Factor
```
Form = Σ(Recent_Results × Weight) / Σ(Weight)
Weight = 1 / (Days_Ago + 1)
```

---

## Công Thức Quản Lý Rủi Ro Nâng Cao

### Công Thức Value at Risk (VaR)
```
VaR = μ - z × σ
Trong đó:
- μ: Lợi nhuận kỳ vọng
- z: Z-score (95% = 1.645, 99% = 2.326)
- σ: Độ lệch chuẩn
```

### Công Thức Conditional Value at Risk (CVaR)
```
CVaR = E[Loss | Loss > VaR]
```

### Công Thức Maximum Drawdown
```
MDD = max(Peak - Trough)
Peak = Giá trị cao nhất
Trough = Giá trị thấp nhất sau Peak
```

### Công Thức Calmar Ratio
```
Calmar_Ratio = Annual_Return / Maximum_Drawdown
```

### Công Thức Sortino Ratio
```
Sortino_Ratio = (Return - Risk_Free_Rate) / Downside_Deviation
```

### Công Thức Information Ratio
```
IR = (Portfolio_Return - Benchmark_Return) / Tracking_Error
```

---

## Công Thức Arbitrage

### Công Thức Arbitrage Cơ Bản
```
Arbitrage = 1/Odds_1 + 1/Odds_2 + ... + 1/Odds_n
Nếu Arbitrage < 1: Có cơ hội arbitrage
Nếu Arbitrage ≥ 1: Không có arbitrage
```

### Công Thức Tính Stake Arbitrage
```
Stake_1 = Total_Stake × (1/Odds_1) / Arbitrage
Stake_2 = Total_Stake × (1/Odds_2) / Arbitrage
...
```

### Công Thức Lợi Nhuận Arbitrage
```
Profit = Total_Stake / Arbitrage - Total_Stake
Profit_Margin = (1 - Arbitrage) × 100%
```

---

## Công Thức Hedging

### Công Thức Hedge Ratio
```
Hedge_Ratio = -Correlation × (σ_Asset / σ_Hedge)
```

### Công Thức Delta Hedge
```
Delta = ∂P/∂S
Hedge_Stake = -Delta × Original_Stake
```

### Công Thức Gamma Hedge
```
Gamma = ∂²P/∂S²
```

---

## Công Thức Martingale

### Công Thức Martingale Cơ Bản
```
Stake_n = Stake_1 × 2^(n-1)
Total_Stake = Stake_1 × (2^n - 1)
```

### Công Thức Martingale Cải Tiến
```
Stake_n = Stake_1 × (1 + f)^(n-1)
Trong đó: f = tỷ lệ tăng (thường = 1)
```

### Công Thức Fibonacci
```
Stake_n = Stake_1 × F_n
F_n = F_(n-1) + F_(n-2)
F_1 = 1, F_2 = 1
```

---

## Công Thức D'Alembert

### Công Thức D'Alembert Cơ Bản
```
Stake_n = Stake_1 + (n-1) × Unit
```

### Công Thức D'Alembert Cải Tiến
```
Stake_n = Stake_1 × (1 + (n-1) × f)
```

---

## Công Thức Labouchere

### Công Thức Labouchere
```
Stake = First_Number + Last_Number
Nếu thắng: Xóa 2 số đầu và cuối
Nếu thua: Thêm stake vào cuối danh sách
```

---

## Công Thức Paroli

### Công Thức Paroli Cơ Bản
```
Stake_n = Stake_1 × 2^(n-1) (nếu thắng)
Stake_n = Stake_1 (nếu thua)
```

---

## Công Thức Oscar's Grind

### Công Thức Oscar's Grind
```
Stake_n = Stake_1 (nếu thắng)
Stake_n = Stake_(n-1) + 1 (nếu thua)
```

---

## Công Thức Weather Betting

### Công Thức Nhiệt Độ
```
P(Temp > T) = 1 - Φ((T - μ) / σ)
Trong đó: Φ = Hàm phân phối chuẩn
```

### Công Thức Lượng Mưa
```
P(Rain > R) = 1 - e^(-λR)
```

### Công Thức Gió
```
P(Wind > W) = 1 - e^(-λW)
```

---

## Công Thức Political Betting

### Công Thức Election Probability
```
P(Candidate_Win) = 1 / (1 + e^(-(β₀ + β₁X₁ + ... + βₙXₙ)))
```

### Công Thức Poll Aggregation
```
P_aggregated = Σ(P_i × Weight_i) / Σ(Weight_i)
Weight_i = 1 / (Error_i)²
```

---

## Công Thức Entertainment Betting

### Công Thức Oscar Awards
```
P(Win) = 1 / (1 + e^(-(β₀ + β₁Critics + β₂BoxOffice + β₃Genre)))
```

### Công Thức Reality TV
```
P(Elimination) = 1 / (1 + e^(-(β₀ + β₁Performance + β₂Popularity)))
```

---

## Công Thức Esports

### Công Thức MOBA (LoL, Dota 2)
```
P(Team_Win) = 1 / (1 + e^(-(β₀ + β₁Gold + β₂Kills + β₃Objectives)))
```

### Công Thức FPS (CS:GO)
```
P(Team_Win) = 1 / (1 + e^(-(β₀ + β₁Rounds + β₂Kills + β₃Economy)))
```

---

## Công Thức Virtual Sports

### Công Thức Virtual Football
```
P(Home_Win) = 1 / (1 + e^(-(β₀ + β₁Form + β₂Strength + β₃Random)))
```

### Công Thức Virtual Horse Racing
```
P(Horse_Win) = 1 / (1 + e^(-(β₀ + β₁Speed + β₂Stamina + β₃Jockey + β₄Random)))
```

---

## Công Thức Cryptocurrency Betting

### Công Thức Bitcoin Price
```
P(Price > P) = 1 - Φ((ln(P) - μ) / σ)
```

### Công Thức Volatility
```
Volatility = σ × √(252) × 100%
```

---

## Công Thức Social Betting

### Công Thức Social Proof
```
P(Bet_Success) = P(Base) × (1 + α × Social_Factor)
```

### Công Thức Influence Weight
```
Influence = Followers × Engagement_Rate × Expertise_Score
```

---

## Ghi Chú Sử Dụng

### Ký Hiệu Thường Dùng
- **P**: Xác suất
- **Odds**: Tỷ lệ cược
- **Stake**: Số tiền cược
- **Payout**: Số tiền thắng
- **λ (lambda)**: Tỷ lệ ghi bàn
- **μ (mu)**: Trung bình
- **σ (sigma)**: Độ lệch chuẩn
- **α (alpha)**: Hệ số học
- **β (beta)**: Hệ số hồi quy

### Đơn Vị Tính
- **Tiền**: VND, USD, EUR
- **Thời gian**: Giây, phút, giờ
- **Xác suất**: 0-1 hoặc 0%-100%
- **Tỷ lệ cược**: Decimal (1.50, 2.00, 3.25)

### Lưu Ý Quan Trọng
1. Luôn kiểm tra điều kiện ràng buộc trước khi áp dụng công thức
2. Làm tròn kết quả theo quy tắc nghiệp vụ
3. Xử lý trường hợp đặc biệt (chia cho 0, giá trị âm)
4. Log tất cả tính toán để debug và audit
5. Cập nhật công thức khi có thay đổi nghiệp vụ

---

**Tài liệu này được tạo tự động từ SPORT_BETTING_MODULE**
**Cập nhật lần cuối: 2024**
**Phiên bản: 1.0**
