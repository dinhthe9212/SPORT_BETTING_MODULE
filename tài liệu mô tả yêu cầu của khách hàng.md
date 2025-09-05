Tài Liệu Tổng Hợp Dự Án Nền Tảng Cá Cược Thể Thao
Giới Thiệu Dự Án
Bối cảnh và Mục tiêu
Trong bối cảnh thị trường cá cược trực tuyến ngày càng phát triển mạnh mẽ, nhu cầu về một nền tảng cá cược thể thao toàn diện, an toàn và hiệu quả trở nên cấp thiết. Các hệ thống hiện có thường đối mặt với những thách thức lớn về quản lý rủi ro tài chính, bảo mật người dùng, và khả năng mở rộng để đáp ứng đa dạng các loại hình cá cược. Dự án này ra đời nhằm giải quyết những vấn đề đó, xây dựng một nền tảng cá cược thể thao tiên tiến, tích hợp các module chuyên biệt để tối ưu hóa trải nghiệm người dùng và đảm bảo lợi nhuận bền vững cho nhà cái.
Mục tiêu chính của dự án là phát triển một hệ thống mạnh mẽ, có khả năng:
•	Cung cấp trải nghiệm cá cược đa dạng: Hỗ trợ nhiều môn thể thao và loại hình cược khác nhau, đáp ứng nhu cầu của mọi đối tượng người chơi.
•	Đảm bảo an toàn và bảo mật: Triển khai hệ thống xác thực và quản lý người dùng chặt chẽ, bảo vệ thông tin cá nhân và tài sản của người chơi.
•	Tối ưu hóa quản lý rủi ro: Xây dựng cơ chế quản lý rủi ro tài chính thông minh, tự động điều chỉnh tỷ lệ cược và ngăn chặn thua lỗ thảm họa cho nhà cái.
•	Mở rộng và linh hoạt: Thiết kế kiến trúc module hóa, cho phép dễ dàng tích hợp các tính năng mới và mở rộng quy mô hệ thống trong tương lai.
Tổng quan về hệ thống
Hệ thống nền tảng cá cược thể thao được thiết kế theo kiến trúc module, bao gồm bốn thành phần chính hoạt động phối hợp chặt chẽ để tạo nên một giải pháp toàn diện:
•	Auth (Hệ Thống Xác Thực và Quản Lý Người Dùng): Đóng vai trò là xương sống về bảo mật và quản lý tài khoản. Module này chịu trách nhiệm xử lý mọi hoạt động liên quan đến đăng ký, đăng nhập, xác thực, phân quyền và bảo vệ dữ liệu người dùng. Auth đảm bảo rằng chỉ những người dùng hợp lệ mới có thể truy cập hệ thống và thực hiện các giao dịch, đồng thời phân định rõ ràng vai trò của từng đối tượng (người dùng, admin, super admin) để áp dụng các chính sách và quyền hạn phù hợp.
•	Betting (Ứng Dụng Cá Cược Thể Thao): Là giao diện chính mà người dùng tương tác. Module này cung cấp các tính năng cốt lõi của một ứng dụng cá cược, bao gồm hiển thị các sự kiện thể thao, các loại cược khả dụng, giao diện đặt cược trực quan, quản lý tài khoản cá nhân, và hiển thị kết quả trận đấu. Betting được thiết kế để mang lại trải nghiệm người dùng mượt mà, dễ sử dụng và hấp dẫn. Đây cũng là module chứa đựng toàn bộ dữ liệu về các môn thể thao, các loại hình cược, và các quy tắc liên quan. Nó cung cấp một danh mục phong phú các bộ môn thể thao (như American Football, Athletics, Australasian Racing, Australian Rules, Badminton, Bandy, Baseball, Basketball, Beach Volleyball, Bowls, Boxing, Chess, Cricket, Cycling, Darts, Esports, Floorball, Futsal, Gaelic Football, Golf, Handball, Hockey, Horse Racing, Ice Hockey, International Rules, Kabaddi, Lacrosse, MMA, Motor Racing, Motorbikes, Netball, Rowing, Rugby League, Rugby Union, Snooker & Pool, Soccer, Special Markets, Speedway, Surfing, Table Tennis, Tennis, Trotting, Volleyball, Water Polo, Winter Sports, Yachting) cùng với các tùy chọn cược đa dạng (Moneyline, Point Spread, Totals, Player Props, Futures, Correct Score, Handicap, Each-Way, Forecast/Exacta, Tricast/Trifecta, Asian Handicap, Over/Under, Half-Time/Full- Time, Cược Phạt Góc, Cược Thẻ Phạt, Cược Hiệp/Nửa trận, Đội Đạt X Điểm Trước, Biên Độ Chiến Thắng, Set Betting, Total Points, End Winner, Method of Victory, Round Betting, Total Rounds, Fight to Go the Distance, Race Winner, Podium Finish, Head-to-Head, To Make/Miss the Cut, First Goal Scorer, Top Batsman, Top Bowler, Man of the Match, Map Winner, Cược Kèo Đặc Thù Game, Cầu Thủ Xuất Sắc Nhất, Frame Handicap, Highest Break, Highest Checkout). Module này đảm bảo rằng hệ thống luôn có sẵn thông tin cập nhật và chi tiết về các sự kiện và lựa chọn cá cược.
•	Quản Lý Rủi Ro Nhà Cái: Là trái tim của hệ thống, chịu trách nhiệm bảo vệ lợi nhuận và sự ổn định tài chính của nhà cái. Module này triển khai các thuật toán phức tạp để quản lý trách nhiệm chi trả (liability), tự động điều chỉnh tỷ lệ cược (dynamic odds) dựa trên dòng tiền, thiết lập ngưỡng rủi ro tối đa, và kích hoạt cơ chế khóa thị trường khẩn cấp khi cần thiết. Module này còn được mở rộng để quản lý rủi ro cho các chương trình khuyến mãi và xử lý các kịch bản phức tạp của cá cược trực tiếp (in-play) thông qua các mô hình toán học chuyên sâu. Mục tiêu là chuyển đổi hoạt động cá cược từ một trò chơi may rủi thành một bài toán quản trị rủi ro tài chính được kiểm soát chặt chẽ, đảm bảo lợi nhuận bền vững trong mọi kịch bản.
•	Sports Data (Module Dữ Liệu Thể Thao): Nguồn cung cấp dữ liệu duy nhất và đáng tin cậy về các sự kiện, giải đấu, tỷ số cho toàn hệ thống.
•	Multi-Currency Wallet (Module Ví Đa Tiền Tệ): Quản lý tài sản và các giao dịch tài chính (nạp/rút/chuyển tiền) của người dùng.
•	Grouping & Community (Module Lập Nhóm & Cộng Đồng): Xây dựng các tính năng xã hội, cho phép người dùng lập nhóm góp vốn và tương tác.
•	Promotions (Module Khuyến Mãi): Cho phép hệ thống và cả người dùng tự tạo các chương trình khuyến mãi để thu hút người chơi.
•	Payment Gateway Integration (Tích Hợp Cổng Thanh Toán): Là một hệ thống con phức tạp, chịu trách nhiệm xử lý dòng tiền ra vào nền tảng một cách an toàn.
Sự kết hợp và tương tác linh hoạt giữa bốn module này tạo nên một nền tảng cá cược thể thao hoàn chỉnh, đáp ứng cả nhu cầu của người chơi về trải nghiệm đa dạng và nhu cầu của nhà cái về quản lý tài chính hiệu quả và an toàn.

Kiến Trúc Hệ Thống
Tổng quan kiến trúc
Hệ thống nền tảng cá cược thể thao được thiết kế theo kiến trúc microservices, cho phép các module hoạt động độc lập nhưng vẫn có khả năng giao tiếp và phối hợp chặt chẽ với nhau. Điều này mang lại sự linh hoạt cao trong phát triển, triển khai và mở rộng hệ thống. Mỗi module chính (Auth, Betting, Quản Lý Rủi Ro) được xem như một service độc lập, có thể được phát triển, triển khai và mở rộng riêng biệt, giảm thiểu sự phụ thuộc và tăng cường khả năng chịu lỗi của toàn hệ thống. Các service này giao tiếp với nhau thông qua các API được định nghĩa rõ ràng, đảm bảo tính nhất quán và khả năng tương thích.
Kiến trúc tổng thể được phân chia thành các tầng logic, mỗi tầng đảm nhiệm một vai trò cụ thể, giúp hệ thống dễ quản lý, bảo trì và phát triển. Sự phân tách này cũng tạo điều kiện thuận lợi cho việc áp dụng các công nghệ khác nhau cho từng tầng hoặc từng service, tối ưu hóa hiệu suất và khả năng mở rộng.

Các tầng kiến trúc
Hệ thống được tổ chức thành bốn tầng kiến trúc chính:
Tầng Presentation (Giao Diện)
Tầng này chịu trách nhiệm cung cấp giao diện người dùng và tương tác trực tiếp với người dùng cuối. Nó bao gồm các ứng dụng web và mobile mà người chơi sử dụng để truy cập và thực hiện các hoạt động cá cược, cũng như các bảng điều khiển quản trị dành cho nhà cái và quản trị viên. Các thành phần chính trong tầng này bao gồm:
•	Betting App: Ứng dụng web và/hoặc mobile dành cho người dùng cuối (người chơi). Đây là nơi người chơi duyệt các sự kiện thể thao, xem tỷ lệ cược, đặt cược, quản lý tài khoản cá nhân, xem lịch sử giao dịch và theo dõi kết quả trận đấu. Giao diện được thiết kế trực quan, thân thiện và đáp ứng trên nhiều thiết bị.
•	Admin Panel: Giao diện quản trị dành cho các nhà cái (admin) và super admin, cung cấp một bộ công cụ toàn diện để vận hành và kiểm soát toàn bộ hệ thống. Các chức năng chính bao gồm:
o	Bảng điều khiển Tổng quan (Dashboard): Hiển thị các chỉ số hiệu suất kinh doanh chính (KPIs) theo thời gian thực như: tổng doanh thu, tổng tiền cược, số lượng người dùng đang hoạt động, tổng trách nhiệm chi trả (liability) hiện tại và lợi nhuận ròng.
o	Quản lý Thị trường và Sự kiện:
	Tạo, xem, và chỉnh sửa thông tin các giải đấu, sự kiện thể thao.
	Quản lý các loại cược (markets) cho từng sự kiện, cho phép mở, đóng, hoặc tạm ngưng một thị trường theo cách thủ công.
o	Công cụ Quản lý Rủi ro Trực quan:
	Giao diện theo dõi trách nhiệm chi trả (liability) theo thời gian thực cho từng sự kiện và từng cửa cược.
	Cho phép admin điều chỉnh thủ công tỷ lệ cược nếu cần.
	Thiết lập và điều chỉnh các Ngưỡng Rủi Ro Tối Đa (Trần Cố Định) cho từng thị trường hoặc sự kiện.
	Xem lại lịch sử các giao dịch bị hệ thống tự động từ chối (phanh khẩn cấp).
o	Quản lý Người dùng:
	Tìm kiếm, xem, và chỉnh sửa thông tin người dùng.
	Quản lý vai trò và phân quyền.
	Theo dõi trạng thái xác minh danh tính (KYC).
o	Quản lý Khuyến mãi: Giao diện để tạo và quản lý các chiến dịch khuyến mãi như Tăng Tỷ Lệ, Cược Miễn Phí. Cho phép gán các ngưỡng rủi ro phụ riêng cho từng chiến dịch.
o	Báo cáo và Phân tích Tài chính:
	Xuất các báo cáo chi tiết về dòng tiền, lịch sử giao dịch, lợi nhuận/lỗ trên từng người chơi, từng sự kiện, từng thị trường.
	Cung cấp các báo cáo phân tích rủi ro chi tiết.
	Giám sát và Báo cáo Sàn Giao Dịch P2P:
	Dashboard Giám sát P2P: Một bảng điều khiển riêng hiển thị các hoạt động trên sàn P2P theo thời gian thực, bao gồm: khối lượng giao dịch, các phiếu cược được giao dịch nhiều nhất, và biến động giá niêm yết.
	Hệ thống Cảnh báo Bất thường: Tự động gửi cảnh báo cho admin khi phát hiện các dấu hiệu thao túng giá hoặc các hoạt động giao dịch bất thường trên sàn P2P.
	Công cụ Quản trị: Cung cấp cho admin khả năng tạm dừng giao dịch P2P cho một sự kiện, một môn thể thao, hoặc toàn bộ thị trường khi có sự cố.
	Báo cáo Giao dịch P2P: Cho phép xuất các báo cáo chi tiết về khối lượng giao dịch, phân tích xu hướng giá của các phiếu cược, và thống kê những người dùng mua/bán tích cực nhất trên sàn.
•	Bảng Điều Khiển Dành Cho Nhà Cái Cá Nhân (Individual Bookmaker Dashboard): Để quản lý rủi ro cho các nhà cái không chuyên, giao diện của họ phải được thiết kế đặc biệt với trọng tâm là giáo dục và cảnh báo, bao gồm các thành phần sau:
o	Cơ Chế Cảnh Báo Trực Quan:
	Hiển thị một thanh đo "Mức Độ Rủi Ro" hoặc "Sức Khỏe Tài Chính" của sự kiện một cách trực quan (ví dụ: Xanh, Vàng, Đỏ).
	Khi các cơ chế bảo vệ tự động như "Dynamic Odds" bị tắt, một cảnh báo lớn, rõ ràng và không thể bỏ qua phải luôn hiển thị trên màn hình.
o	Giao diện lựa chọn bắt buộc: Hệ thống sẽ hiển thị một màn hình yêu cầu người dùng chọn một trong hai phương án:
	Phương án 1 (mặc định): Tự quản lý rủi ro thủ công. Kèm theo cảnh báo rõ ràng (⚠️): Hệ thống sẽ KHÔNG tự động điều chỉnh tỷ lệ cược. Bạn phải tự theo dõi và điều chỉnh thủ công.
	Phương án 2: Kích hoạt bảo vệ tự động. Mô tả rõ: Hệ thống sẽ tự động điều chỉnh tỷ lệ cược (Dynamic Odds) và yêu cầu thiết lập một Ngưỡng Rủi Ro Tối Đa để bảo vệ vốn.
o	Xác Nhận Rủi Ro (Risk Acknowledgment):
	Nếu người dùng chọn Phương án 2, hệ thống sẽ yêu cầu một bước xác nhận thứ cấp, buộc họ phải gõ một chuỗi văn bản như "Tôi chấp nhận rủi ro" để đảm bảo họ đã đọc và hiểu rõ cảnh báo. Nút "Tiếp tục" sẽ bị vô hiệu hóa cho đến khi người dùng hoàn thành bước này.
•	Các Thành Phần Giao Diện Nâng Cao:
o	Hệ thống Băng chuyền Sản phẩm (Product Carousel): Để nâng cao trải nghiệm, thúc đẩy tương tác và đảm bảo tính công bằng, giao diện sẽ triển khai một hệ thống băng chuyền sản phẩm cược thông minh, năng động và lấy người dùng làm trung tâm. Hệ thống này hoạt động dựa trên các quy tắc vận hành cốt lõi sau:
o	1. Quy tắc Phân Loại và Ưu Tiên Hiển Thị (Đảm bảo Công bằng):
	Phân loại trạng thái: Mỗi sản phẩm cược được gắn một trạng thái: chưa_mua hoặc đã_mua.
	Ưu tiên tuyệt đối: Hệ thống luôn xếp tất cả sản phẩm có trạng thái chưa_mua lên đầu, theo sau là các sản phẩm đã_mua.
	Ngẫu nhiên hóa: Trong cùng một nhóm trạng thái (chưa_mua hoặc đã_mua), thứ tự sản phẩm sẽ được xáo trộn ngẫu nhiên mỗi khi làm mới để đảm bảo mọi sản phẩm đều có cơ hội xuất hiện ở các vị trí khác nhau.
o	2. Quy tắc Hành Vi Tự Động của Hệ Thống:
	Tự động chạy (Auto-play): Băng chuyền sẽ tự động lướt qua các sản phẩm tuần tự với một khoảng thời gian được thiết lập (ví dụ: 5 giây cho 5 sản phẩm).
	Tự động làm mới (Auto-Refresh): Sau khi chạy đến sản phẩm cuối cùng, băng chuyền sẽ tạm dừng ngắn (5 giây), sau đó tự động tải về một chuỗi sản phẩm ngẫu nhiên mới (vẫn tuân thủ quy tắc ưu tiên) để tạo ra sự mới mẻ liên tục.
o	3. Quy tắc Tương Tác Của Người Dùng:
	Dừng khi rê chuột (Pause on Hover): Khi người dùng di chuyển con trỏ chuột vào khu vực băng chuyền, quá trình tự động chạy sẽ dừng lại ngay lập tức và tiếp tục khi chuột di chuyển ra ngoài.
	Nút "Làm mới": Cung cấp một nút bấm trực quan để người dùng chủ động làm mới băng chuyền và nhận một chuỗi sản phẩm ngẫu nhiên mới.
o	4. Quy tắc Cập Nhật Trạng Thái Thời Gian Thực:
	Khi một đơn hàng được xác nhận thành công, trạng thái của sản phẩm đó phải được cập nhật ngay từ chưa_mua thành đã_mua. Hệ thống nên cập nhật trực tiếp trên giao diện mà không cần tải lại trang.
o	5. Tối ưu hóa số lượng sản phẩm hiển thị:
Loại thiết bị	Số sản phẩm hiển thị 1 lần	Tổng số sản phẩm trong băng chuyền
Máy tính (Desktop)	4.5 sản phẩm	20 sản phẩm
Máy tính bảng (Tablet)	4.5 sản phẩm	20 sản phẩm
Di động (Mobile)	2.5 sản phẩm (Luôn để lộ một phần sản phẩm tiếp theo để khuyến khích vuốt)	15 sản phẩm
o	Bảng Xếp Hạng (Leaderboards): Cung cấp các bảng xếp hạng công khai để vinh danh 100 cá nhân và 100 nhóm có mức lợi nhuận cao nhất theo ngày, tuần, tháng, quý và năm. Tính năng này không chỉ tạo ra sự cạnh tranh lành mạnh mà còn giúp người chơi mới nhận diện các nhà cái uy tín.

Tầng Business Logic (Logic Nghiệp Vụ)
Tầng này chứa đựng các quy tắc và logic nghiệp vụ cốt lõi của hệ thống. Đây là nơi các yêu cầu từ tầng Presentation được xử lý, các tính toán được thực hiện, và các quyết định nghiệp vụ được đưa ra. Tầng Business Logic được chia thành các microservices chuyên biệt:
•	Auth Service: Dịch vụ xác thực và quản lý người dùng. Chịu trách nhiệm xử lý đăng ký, đăng nhập, xác thực phiên, quản lý vai trò và phân quyền, cũng như bảo mật thông tin người dùng. Mọi yêu cầu liên quan đến người dùng đều được xử lý qua service này.
•	Betting Service: Dịch vụ xử lý các hoạt động cá cược. Bao gồm logic cho việc đặt cược, xác nhận cược, tính toán kết quả cược, và xử lý thanh toán. Service này tương tác chặt chẽ với Risk Management Service để lấy tỷ lệ cược và kiểm tra tính hợp lệ của cược.
•	Risk Management Service: Dịch vụ quản lý rủi ro tài chính. Đây là service phức tạp nhất, chịu trách nhiệm tính toán trách nhiệm chi trả, điều chỉnh tỷ lệ cược động, áp dụng ngưỡng rủi ro và kích hoạt cơ chế khóa thị trường. Service này đảm bảo rằng nhà cái luôn duy trì lợi nhuận và tránh được các khoản lỗ lớn.
•	Sports Data Service: Dịch vụ quản lý dữ liệu về các môn thể thao, sự kiện, và các loại cược. Service này cung cấp thông tin chi tiết về các trận đấu, tỷ lệ cược ban đầu, và các quy tắc cược cho Betting Service và Risk Management Service.
•	Giải pháp cho Tính nhất quán Dữ liệu (Saga Pattern)
Trong kiến trúc microservices với mô hình database-per-service, việc đảm bảo một giao dịch nghiệp vụ (ví dụ: đặt cược) diễn ra thành công qua nhiều service (ví dụ: Betting Service và Wallet Service) đòi hỏi một giải pháp chuyên biệt. Hệ thống sẽ áp dụng Saga Pattern để giải quyết vấn đề này.
o	Khái niệm: Một Saga là một chuỗi các giao dịch cục bộ. Nếu một bước trong chuỗi thất bại, Saga sẽ thực thi các giao dịch bù trừ để hoàn tác các bước đã thành công trước đó, đảm bảo dữ liệu toàn hệ thống không rơi vào trạng thái không nhất quán.
o	Luồng Đặt cược áp dụng Saga (Dựa trên Choreography):
1.	Betting Service: Khi nhận yêu cầu đặt cược, service này tạo một bản ghi cược với trạng thái ĐANG_CHỜ (PENDING) trong CSDL của mình, sau đó phát ra sự kiện BetPlaced vào Message Queue. Sự kiện này chứa thông tin về ID người dùng, số tiền cần trừ, ID cược, ...
2.	Wallet Service: Lắng nghe sự kiện BetPlaced từ Message Queue, thực hiện giao dịch trừ tiền trong CSDL của mình.
o	Nếu thành công, Wallet Service phát ra sự kiện FundsDebited.
o	Nếu thất bại (không đủ tiền), Wallet Service phát ra sự kiện DebitFailed.
3.	Betting Service (Hoàn tất):
o	Lắng nghe sự kiện FundsDebited và cập nhật trạng thái cược thành ĐÃ_XÁC_NHẬN. Giao dịch thành công.
o	Lắng nghe sự kiện DebitFailed và thực hiện giao dịch bù trừ: cập nhật trạng thái cược thành ĐÃ_HỦY. Giao dịch thất bại nhưng hệ thống vẫn nhất quán.
o	Lộ trình: Hệ thống sẽ bắt đầu với mô hình Saga dựa trên Choreography (các service tự phối hợp qua message queue). Khi các quy trình trở nên phức tạp hơn, việc xây dựng một Saga Orchestrator (bộ điều phối trung tâm) sẽ được cân nhắc Áp dụng vào luồng đặt cược:
	Một service mới tên là OrderService hoặc SagaOrchestrator được tạo ra.
	Người dùng đặt cược, yêu cầu được gửi đến OrderService.
	OrderService bắt đầu chỉ huy:
	Gửi lệnh đến Betting Service: "Tạo một cược với trạng thái PENDING".
	Sau khi Betting Service xác nhận, OrderService gửi lệnh đến Wallet Service: "Trừ tiền cho cược này".
	Nếu Wallet Service báo thành công, OrderService gửi lệnh cuối cùng đến Betting Service: "Xác nhận cược".
	Nếu Wallet Service báo thất bại, OrderService gửi lệnh bù trừ đến Betting Service: "Hủy cược".
Tầng Data (Dữ Liệu)
Tầng Data chịu trách nhiệm lưu trữ và quản lý tất cả dữ liệu của hệ thống. Mỗi service trong tầng Business Logic có thể có cơ sở dữ liệu riêng của mình (database-per-service pattern) để tăng tính độc lập và khả năng mở rộng. Các loại cơ sở dữ liệu có thể được sử dụng bao gồm:
•	User Database: Lưu trữ thông tin người dùng, thông tin đăng nhập, vai trò, quyền hạn và các dữ liệu cá nhân khác liên quan đến Auth Service.
•	Sports Database: Chứa dữ liệu về các môn thể thao, giải đấu, đội/vận động viên, lịch thi đấu, và các loại cược khả dụng, được quản lý bởi Sports Data Service.
•	Transaction Database: Ghi lại tất cả các giao dịch cá cược, lịch sử đặt cược, kết quả cược, và thông tin thanh toán, được quản lý bởi Betting Service.
•	Risk Database: Lưu trữ các tham số quản lý rủi ro, lịch sử thay đổi tỷ lệ cược, và các dữ liệu liên quan đến trách nhiệm chi trả, được quản lý bởi Risk Management Service.
Tầng Integration (Tích Hợp)
Tầng Integration đảm bảo sự giao tiếp thông suốt giữa các service nội bộ và với các hệ thống bên ngoài. Tầng này bao gồm các thành phần giúp điều phối luồng dữ liệu và xử lý các tác vụ bất đồng bộ:
•	API Gateway: Điểm truy cập duy nhất cho tất cả các yêu cầu từ tầng Presentation. API Gateway chịu trách nhiệm định tuyến yêu cầu đến các service phù hợp, thực hiện xác thực cơ bản, và tổng hợp phản hồi từ nhiều service nếu cần. Điều này giúp ẩn đi sự phức tạp của kiến trúc microservices từ phía client.
•	Message Queue (MQ): Được sử dụng để xử lý các tác vụ bất đồng bộ và giao tiếp giữa các service một cách đáng tin cậy, nó có thể đưa thông tin này vào một hàng đợi. Các service khác sẽ lắng nghe hàng đợi này và xử lý dữ liệu mà không làm chậm trễ quá trình thu thập dữ liệu gốc. Ví dụ, khi một cược được đặt, Betting Service có thể gửi một thông báo đến MQ, và Risk Management Service sẽ nhận thông báo đó để xử lý tính toán rủi ro mà không làm chậm quá trình đặt cược của người dùng.
•	Cache Layer: Lớp bộ nhớ đệm được sử dụng để lưu trữ tạm thời các dữ liệu thường xuyên được truy cập (ví dụ: tỷ lệ cược hiện tại, thông tin sự kiện phổ biến) nhằm giảm tải cho cơ sở dữ liệu, tiết kiệm API call và tăng tốc độ phản hồi của hệ thống.
•	External APIs: Các giao diện lập trình ứng dụng bên ngoài. Dữ liệu này có thể được nhập thủ công hoặc thông qua tích hợp với các API dữ liệu thể thao bên ngoài (ví dụ: các nhà cung cấp dữ liệu tỷ số trực tiếp, kết quả trận đấu, thông tin cầu thủ, thống kê trận đấu, lịch sử đối đầu, tin tức thể thao) hoặc các hệ thống thanh toán bên ngoài (ví dụ: cổng thanh toán, dịch vụ ví điện tử, ngân hàng). Điều này giúp hệ thống luôn có dữ liệu cập nhật và chính xác.
Tích Hợp Cổng Thanh Toán (Payment Gateway Integration)
Module này không chỉ là một kết nối API đơn thuần mà là một hệ thống con phức tạp để quản lý toàn bộ dòng tiền của nền tảng.
•	Chức năng cốt lõi: Xử lý an toàn và hiệu quả các giao dịch nạp tiền (deposit) và rút tiền (withdrawal) của người dùng thông qua các nhà cung cấp dịch vụ thanh toán bên ngoài.
•	Các yêu cầu và tính năng chi tiết:
o	Chiến lược Đa nhà cung cấp: Tích hợp với nhiều cổng thanh toán khác nhau (thẻ tín dụng, ví điện tử, chuyển khoản ngân hàng, tiền mã hóa) để cung cấp nhiều lựa chọn cho người dùng và làm phương án dự phòng khi một cổng gặp sự cố.
o	Quản lý Giao dịch Tập trung: Xây dựng một service nội bộ để quản lý tất cả các giao dịch, bất kể chúng được thực hiện qua cổng thanh toán nào. Service này sẽ theo dõi trạng thái của từng giao dịch (đang chờ, thành công, thất bại, đã hoàn tiền).
o	Xử lý Hoàn tiền và Tranh chấp (Chargeback & Dispute): 
	QUY TRÌNH XỬ LÝ TRANH CHẤP VÀ CHARGEBACK
Đây là quy trình vận hành chuẩn để xử lý các khiếu nại của người dùng liên quan đến giao dịch tài chính và các yêu cầu đòi lại tiền (chargeback) từ ngân hàng.
	Các bên liên quan chính:
	Bộ phận Hỗ trợ Khách hàng (CS): Tuyến xử lý Level 1.
	Bộ phận Thanh toán & Rủi ro: Tuyến xử lý chuyên sâu Level 2.
	Quy trình chi tiết gồm 6 bước:
	Bước 1: Tiếp Nhận Khiếu Nại
Người dùng khiếu nại qua kênh chính thức là "Trung tâm Hỗ trợ" hoặc "Khiếu nại Giao dịch" trong tài khoản. Yêu cầu được tạo dưới dạng một phiếu (ticket) trong hệ thống ticket (phiếu yêu cầu) có cấu trúc, yêu cầu người dùng điền các thông tin cơ bản: ID giao dịch, lý do khiếu nại, mô tả chi tiết và chuyển đến đội CS. Tránh xử lý qua các kênh không chính thức như chat mạng xã hội.
	Bước 2: Phản Hồi và Giải Quyết Sơ Bộ (Level 1)
Đội CS xem xét khiếu nại của người dùng, đối chiếu thông tin với dữ liệu giao dịch cơ bản và liên hệ lại với người dùng để giải thích. Nếu lỗi thuộc về hệ thống (ví dụ: lỗi kỹ thuật rõ ràng), đội CS có thể được trao quyền để tiến hành hoàn tiền trực tiếp cho người dùng. Nếu người dùng không đồng ý hoặc họ đã khiếu nại thẳng lên ngân hàng của họ, vụ việc sẽ được chuyển sang Bước 3. Mục tiêu là giải quyết vấn đề trực tiếp để ngăn chặn leo thang thành chargeback. 
	Bước 3: Nhận Thông Báo Chargeback và Xử Lý Tài Khoản
Khi người dùng khiếu nại qua ngân hàng của họ, nền tảng sẽ nhận thông báo chargeback chính thức từ cổng thanh toán, đội Thanh toán & Rủi ro phải ngay lập tức TẠM KHÓA tài khoản của người dùng khiếu nại để ngăn chặn các rủi ro phát sinh thêm. Ngăn người dùng rút các khoản tiền khác trong tài khoản. Ngăn người dùng tiếp tục sử dụng dịch vụ và có thể gây ra thêm các tranh chấp khác. Bảo vệ nền tảng khỏi rủi ro lạm dụng.
	Bước 4: Thu Thập Bằng Chứng Chuyên Sâu (Level 2)
Đội Thanh toán & Rủi ro tổng hợp một bộ hồ sơ bằng chứng chi tiết, bao gồm:
	Thông tin Giao dịch: ID, số tiền, ngày giờ, phương thức thanh toán.
	Thông tin Người dùng: User ID, email, ngày đăng ký, địa chỉ IP đã sử dụng khi đăng ký và khi thực hiện giao dịch.
	Lịch sử Hoạt động: Nhật ký đăng nhập, lịch sử các giao dịch nạp/rút/cược thành công trước đó (để chứng minh người dùng đã quen thuộc và tự nguyện sử dụng dịch vụ).
	Bằng chứng Sử dụng Dịch vụ (Cực kỳ quan trọng với ngành cược): 
	Snapshot của phiếu cược: ID phiếu cược, cửa cược, loại cược.
	Snapshot của tỷ lệ cược (odds) tại đúng thời điểm người dùng nhấn nút đặt cược.
	Log hệ thống xác nhận Risk Management Service đã chấp nhận cược đó.
	Log hệ thống về kết quả chính thức của sự kiện thể thao (ví dụ: tỷ số cuối cùng).
	Log hệ thống về kết quả của phiếu cược (thắng/thua) và giao dịch cộng tiền vào ví nếu thắng.
	Bằng chứng về sự Đồng ý Điều khoản: Log hệ thống ghi lại thời điểm người dùng đồng ý với "Điều khoản Dịch vụ" khi đăng ký tài khoản.
	Bước 5: Gửi Phản Hồi Tranh Chấp
Toàn bộ hồ sơ bằng chứng được tổng hợp và gửi lại cho cổng thanh toán trước thời hạn quy định.
	Bước 6: Chờ Phán Quyết và Xử Lý Kết Quả
	Nếu nền tảng thắng: Khoản tiền chargeback sẽ được hoàn lại. Tài khoản người dùng sẽ được xem xét. Nếu đây là hành vi lạm dụng, tài khoản nên bị khóa vĩnh viễn.
	Nếu nền tảng thua: Nền tảng mất số tiền đó và phải trả thêm một khoản phí phạt chargeback. Tài khoản người dùng phải bị khóa vĩnh viễn và thông tin của họ nên được đưa vào danh sách đen (blacklist) để ngăn chặn đăng ký lại.
o	Quản lý Phí giao dịch: Cấu hình linh hoạt để xử lý phí giao dịch từ các cổng thanh toán (có thể do nền tảng chịu, người dùng chịu, hoặc chia sẻ).
o	Hỗ trợ Đa tiền tệ: Hệ thống phải có khả năng xử lý các giao dịch bằng nhiều loại tiền tệ khác nhau, bao gồm việc quản lý tỷ giá hối đoái và quy trình thanh toán (settlement) với các nhà cung cấp.
o	Bảo mật: Tuân thủ nghiêm ngặt tiêu chuẩn PCI DSS cho các giao dịch thẻ và mã hóa toàn bộ dữ liệu giao dịch nhạy cảm.
Kiến trúc này đảm bảo một hệ thống mạnh mẽ, có khả năng mở rộng, dễ bảo trì và có tính sẵn sàng cao, đáp ứng được yêu cầu của một nền tảng cá cược thể thao hiện đại.

Các Yêu Cầu Phi Chức Năng
Đây là các yêu cầu thiết yếu để đảm bảo hệ thống hoạt động ổn định, an toàn và hiệu quả.
•	Hiệu Suất (Performance):
o	Thời gian phản hồi (Latency):
	Thời gian xử lý một giao dịch đặt cược (từ khi người dùng nhấn "xác nhận" đến khi nhận được phản hồi) phải dưới 500ms.
	Thời gian cập nhật tỷ lệ cược mới trên giao diện người dùng phải dưới 1 giây kể từ thời điểm hệ thống nhận được dữ liệu mới từ API bên ngoài. Tần suất cập nhật tổng thể và độ trễ của dữ liệu sẽ phụ thuộc vào chu kỳ làm mới của các nhà cung cấp API đã chọn trong từng giai đoạn.
o	Khả năng chịu tải (Concurrency):
	Hệ thống phải có khả năng xử lý ít nhất 1,000 người dùng hoạt động đồng thời và 200 giao dịch đặt cược mỗi giây trong điều kiện bình thường.
	Trong các sự kiện thể thao lớn (ví dụ: Chung kết World Cup, Super Bowl), hệ thống phải có khả năng mở rộng để xử lý lượng truy cập tăng gấp 5-10 lần mà không ảnh hưởng đến hiệu suất.
o	Độ sẵn sàng (Availability): Hệ thống phải đạt độ sẵn sàng 99.9% (tổng thời gian "sập" hệ thống không quá 8.77 giờ mỗi năm).
•	Bảo Mật Chi Tiết (Detailed Security):
o	Tuân thủ quy định: Ngoài việc tuân thủ các quy định về bảo vệ dữ liệu như GDPR, nếu hệ thống xử lý thanh toán qua thẻ tín dụng, nó phải tuân thủ nghiêm ngặt tiêu chuẩn 
•	Giám Sát và Vận Hành (Monitoring and Operations)
Để đảm bảo hệ thống hoạt động ổn định, hiệu quả và nhanh chóng phát hiện sự cố, một chiến lược giám sát toàn diện dựa trên "Ba Trụ cột của Khả năng Quan sát" sẽ được triển khai:
o	Logging (Ghi Log Tập Trung): Tất cả các microservices sẽ ghi log theo định dạng JSON có cấu trúc. Các log này sẽ được thu thập và tập trung tại một nơi duy nhất (ví dụ: Loki) để dễ dàng tìm kiếm và phân tích khi có sự cố.
o	Metrics (Thu Thập Số Liệu): Sử dụng Prometheus để thu thập các số liệu vận hành theo thời gian thực. Các số liệu này bao gồm:
	Metrics Hệ thống: Độ trễ API, tỷ lệ lỗi, mức sử dụng CPU/RAM của từng service.
	Metrics Nghiệp vụ: Số lượng cược mỗi giây, doanh thu, số người dùng đang hoạt động, độ sâu của hàng đợi Kafka.
o	Tracing (Truy Vết Phân Tán): Sử dụng OpenTelemetry hoặc Jaeger để theo dõi hành trình của một yêu cầu khi nó đi qua nhiều service khác nhau. Điều này cực kỳ quan trọng để chẩn đoán các vấn đề về hiệu suất trong kiến trúc microservices.
o	Alerting (Cảnh Báo): Thiết lập hệ thống cảnh báo tự động (sử dụng Alertmanager) dựa trên các ngưỡng của metrics đã thu thập. Ví dụ: cảnh báo khi tỷ lệ lỗi của API Gateway vượt quá 2% trong 5 phút, hoặc khi một nguồn dữ liệu thể thao ngừng phản hồi.

PCI DSS (Payment Card Industry Data Security Standard).
o	Mã hóa:
	Tất cả dữ liệu nhạy cảm của người dùng (mật khẩu, thông tin cá nhân) phải được mã hóa khi lưu trữ trong cơ sở dữ liệu (encryption-at-rest).
	Tất cả dữ liệu truyền đi giữa client và server, cũng như giữa các microservices, phải được mã hóa bằng giao thức TLS 1.2 trở lên (encryption-in-transit).
o	Kiểm tra và Đánh giá: Hệ thống phải được kiểm tra thâm nhập (penetration testing) và đánh giá lỗ hổng bảo mật định kỳ (tối thiểu mỗi 6 tháng một lần hoặc sau mỗi lần cập nhật lớn).
•	Kế Hoạch Sao Lưu và Phục Hồi Sau Thảm Họa (Backup and Disaster Recovery):
o	Mục tiêu Phục hồi (Recovery Objectives):
	RPO (Recovery Point Objective): Mức độ mất mát dữ liệu tối đa có thể chấp nhận được. Đối với Transaction Database, RPO phải là 15 phút. Đối với các cơ sở dữ liệu ít thay đổi hơn như User Database, RPO có thể là 1 giờ.
	RTO (Recovery Time Objective): Thời gian tối đa để khôi phục lại hoạt động của hệ thống sau sự cố. RTO được đặt ra là 2 giờ.
o	Chiến lược sao lưu:
	Transaction Database và Risk Database phải được sao lưu liên tục (point-in-time recovery).
	User Database và Sports Database phải được sao lưu toàn bộ hàng ngày và sao lưu các thay đổi (incremental backup) mỗi giờ.
o	Kiểm tra phục hồi: Kế hoạch phục hồi phải được kiểm tra thực tế ít nhất mỗi quý một lần để đảm bảo tính hiệu quả và sẵn sàng khi có sự cố thật xảy ra.

Tuân Thủ Pháp Lý và Quy Định (Regulatory Compliance)
Hệ thống phải được thiết kế với khả năng tùy biến để tuân thủ các quy định pháp lý khác nhau tại từng thị trường mục tiêu. Các yêu cầu cốt lõi bao gồm:
•	Xác minh Danh tính Khách hàng (KYC - Know Your Customer):
o	Hệ thống phải có quy trình cho phép người dùng tải lên các tài liệu nhận dạng (ví dụ: CMND/CCCD, hộ chiếu) và chứng minh địa chỉ.
o	Xác minh danh tính thủ công quy trình kiểm tra.
o	Phân cấp các trạng thái tài khoản (chưa xác minh, đang chờ, đã xác minh) và áp dụng các giới hạn giao dịch tương ứng.
•	Chống Rửa tiền (AML - Anti-Money Laundering):
o	Hệ thống phải có khả năng giám sát các giao dịch để phát hiện các hoạt động đáng ngờ (ví dụ: nạp/rút tiền lớn bất thường, các mẫu cược lạ).
o	Tự động gắn cờ (flag) các tài khoản hoặc giao dịch đáng ngờ để đội ngũ tuân thủ xem xét thủ công.
o	Lưu trữ hồ sơ giao dịch chi tiết để phục vụ cho việc kiểm toán và báo cáo cho các cơ quan chức năng khi được yêu cầu.
•	Cá cược có Trách nhiệm (Responsible Gaming):
o	Cung cấp cho người chơi các công cụ để tự kiểm soát hoạt động cá cược của mình, bao gồm:
	Tự đặt giới hạn: Cho phép người chơi tự đặt ra giới hạn về số tiền nạp, số tiền cược, và số tiền thua trong một khoảng thời gian (ngày/tuần/tháng).
	Tạm nghỉ (Time-Out): Cho phép người chơi tự khóa tài khoản tạm thời trong một khoảng thời gian ngắn (ví dụ: 24 giờ, 1 tuần).
	Tự loại trừ (Self-Exclusion): Cho phép người chơi tự khóa tài khoản vĩnh viễn hoặc trong một thời gian dài (ví dụ: 6 tháng, 1 năm).
o	Hiển thị thông báo và lời nhắc về thời gian chơi để nâng cao nhận thức cho người dùng.
•	Phân Tích Sâu về Cơ Chế Giám Sát và Yêu cầu Báo cáo Dữ liệu
Để hoạt động hợp pháp tại các thị trường được quản lý, nền tảng phải tuân thủ các cơ chế giám sát và yêu cầu báo cáo dữ liệu nghiêm ngặt từ cơ quan chức năng.
o	A. Các Cơ Chế Giám Sát Cốt Lõi trong Quy trình Cấp Phép:
	Thẩm định ban đầu: Bao gồm kiểm tra sức khỏe tài chính để đảm bảo khả năng chi trả và thẩm định lý lịch của ban lãnh đạo.
	Giám sát Kỹ thuật và an ninh Thông tin (Ongoing Technical Audits): Hệ thống phải được kiểm toán kỹ thuật định kỳ về an toàn dữ liệu người dùng, khả năng chống tấn công mạng và tính công bằng của các thuật toán. * 
	Giám sát Việc Thực thi Trách nhiệm Xã hội: Cơ quan quản lý sẽ kiểm tra để đảm bảo các công cụ "Cá cược có Trách nhiệm" hoạt động hiệu quả, có thể yêu cầu báo cáo về số lượng người dùng tự đặt giới hạn hoặc tự loại trừ.
	Giám sát Quy trình Chống Rửa tiền (AML) và Xác minh Khách hàng (KYC): Kiểm tra tính hiệu quả của quy trình KYC và khả năng của hệ thống trong việc phát hiện, báo cáo các giao dịch đáng ngờ.
o	B. Danh sách Chi tiết Dữ liệu Báo cáo qua API:
Khi kết nối trực tiếp với hệ thống của cơ quan quản lý, các nhóm dữ liệu sau thường được yêu cầu cung cấp:
	1. Dữ liệu về Người chơi:
ID người chơi (đã được mã hóa hoặc ẩn danh)
Quốc gia cư trú
Ngày đăng ký
Trạng thái xác minh danh tính (KYC Status)
	2. Dữ liệu về Giao dịch Tài chính:
Mỗi giao dịch Nạp/Rút tiền phải được báo cáo, bao gồm: ID giao dịch, ngày giờ, số tiền, tiền tệ, phương thức thanh toán, và trạng thái giao dịch.
	3. Dữ liệu về Hoạt động Cá cược (Quan trọng nhất cho việc tính thuế):
Mỗi phiếu cược được đặt: ID phiếu cược, ID người chơi, ngày giờ, số tiền cược (Stake), thông tin sự kiện và thị trường, tỷ lệ cược (Odds) tại thời điểm đặt.
Mỗi khi thanh toán một phiếu cược: ID phiếu cược, kết quả (Thắng/Thua/Hòa/Hủy), và số tiền trả thưởng (Payout).
	4. Dữ liệu về Trách nhiệm Xã hội: 
Số liệu thống kê ẩn danh về việc sử dụng các công cụ Cá cược có Trách nhiệm (số người đặt giới hạn, số người tự loại trừ).
Số lượng các cảnh báo về hành vi đáng ngờ (AML) đã được hệ thống tạo ra.

Kiến trúc Kỹ thuật cho Việc Tuân thủ Linh hoạt
Để hệ thống có thể thích ứng với các quy định pháp lý khác nhau tại từng thị trường, chúng tôi sẽ xây dựng một Compliance Service chuyên biệt.
•	Cơ sở dữ liệu Quy tắc: Một bảng trong CSDL sẽ lưu trữ các quy tắc (ví dụ: max_deposit_per_day, is_kyc_required) theo từng khu vực pháp lý (quốc gia).
•	Cơ chế Policy Engine: Compliance Service sẽ hoạt động như một "policy engine". Các service khác (Auth, Betting) khi cần thực hiện một hành động nhạy cảm (như đăng ký, nạp/rút tiền) sẽ gửi yêu cầu kiểm tra đến service này.
•	Tính linh hoạt: Compliance Service sẽ dựa vào khu vực pháp lý của người dùng để tải các quy tắc tương ứng và trả về kết quả cho phép hoặc từ chối. Điều này cho phép đội ngũ vận hành cập nhật các quy định mới bằng cách thay đổi dữ liệu trong CSDL mà không cần triển khai lại code.

Các Module Chính và Chức Năng
Hệ thống được xây dựng dựa trên sự phối hợp chặt chẽ của bốn module chính, mỗi module đảm nhiệm một vai trò và tập hợp các chức năng riêng biệt, tạo nên một nền tảng cá cược thể thao toàn diện và hiệu quả.
Module Xác Thực và Quản Lý Người Dùng (Auth)
•	Chức năng chính: Auth là trái tim của hệ thống về mặt bảo mật và quản lý danh tính. Nó cung cấp một giải pháp toàn diện cho việc xác thực, ủy quyền và quản lý thông tin người dùng, đảm bảo rằng mọi tương tác trong hệ thống đều được kiểm soát và bảo vệ chặt chẽ.
•	Vai trò trong hệ thống: Module này đóng vai trò nền tảng, cung cấp dịch vụ xác thực và quản lý người dùng cho tất cả các module khác. Mọi người dùng, từ người chơi cá nhân đến các cấp quản trị (admin, super admin), đều phải thông qua Auth để truy cập và sử dụng hệ thống. Điều này tạo ra một lớp bảo mật tập trung và nhất quán.
•	Các tính năng chi tiết:
o	Đăng ký và Đăng nhập: Cung cấp quy trình đăng ký tài khoản mới an toàn và dễ dàng, bao gồm xác minh email/số điện thoại. Hỗ trợ các phương thức đăng nhập đa dạng (tên người dùng/mật khẩu, đăng nhập xã hội, sinh trắc học, xác thực đa yếu tố) với các biện pháp bảo mật như mã hóa mật khẩu và kiểm tra brute-force.
o	Xác thực và Ủy quyền: Quản lý phiên đăng nhập, sử dụng token (ví dụ: JWT) để xác thực các yêu cầu API. Áp dụng các chính sách ủy quyền dựa trên vai trò (Role- Based Access Control - RBAC) để đảm bảo người dùng chỉ có thể truy cập các tài nguyên và thực hiện các hành động mà họ được phép.
o	Quản lý Phân quyền và Vai trò Người dùng: Định nghĩa và quản lý các vai trò khác nhau trong hệ thống (ví dụ: player, admin , super_admin ,risk_manager). Mỗi vai trò có một tập hợp các quyền hạn cụ thể, giúp kiểm soát chặt chẽ quyền truy cập vào các chức năng và dữ liệu nhạy cảm.
o	Bảo mật Tài khoản và Dữ liệu Cá nhân: Triển khai các biện pháp bảo mật tiên tiến như mã hóa dữ liệu nhạy cảm (ví dụ: thông tin cá nhân, lịch sử giao dịch), bảo vệ chống lại các cuộc tấn công phổ biến (SQL Injection, XSS), và tuân thủ các quy định về bảo vệ dữ liệu (ví dụ: GDPR). Để ngăn chặn hành vi lạm dụng và thao túng, hệ thống sẽ triển khai thêm các cơ chế kiểm soát nâng cao:
	Giám sát và Hạn chế theo Địa chỉ IP và Thiết bị: Hệ thống sẽ theo dõi địa chỉ IP và sử dụng công nghệ "device fingerprinting" (nhận dạng thiết bị) để phát hiện các tài khoản đáng ngờ được tạo và truy cập từ cùng một nguồn. Các hành vi bất thường sẽ bị gắn cờ để xem xét thủ công.
	Xác thực Danh tính Nâng cao: Đối với các giao dịch có giá trị cao hoặc các hoạt động trên Sàn Giao Dịch P2P, hệ thống có thể yêu cầu người dùng hoàn thành quy trình xác minh danh tính nâng cao (KYC level 2) để đảm bảo mỗi người dùng chỉ vận hành một tài khoản chính.
o	Quản lý Hồ sơ Người dùng: Cho phép người dùng xem và cập nhật thông tin cá nhân, thay đổi mật khẩu, quản lý các tùy chọn bảo mật (ví dụ: xác thực hai yếu tố - 2FA, câu hỏi bảo mật, mã dự phòng).
Module Ứng Dụng Cá Cược (Betting)
•	Chức năng chính: Betting là giao diện chính và trung tâm tương tác của người dùng với nền tảng cá cược. Nó cung cấp một môi trường trực quan và đầy đủ tính năng để người chơi khám phá, đặt cược và theo dõi các sự kiện thể thao. Module này cũng là kho lưu trữ và quản lý toàn bộ dữ liệu liên quan đến các môn thể thao, các sự kiện, và các loại hình cá cược. Nó đảm bảo rằng hệ thống luôn có nguồn dữ liệu phong phú, chính xác và cập nhật để cung cấp cho người dùng và các module nghiệp vụ khác.
•	Vai trò trong hệ thống: Module này đóng vai trò là tầng Presentation và một phần của tầng Business Logic, chịu trách nhiệm hiển thị thông tin, tiếp nhận yêu cầu từ người dùng và chuyển tiếp đến các service nghiệp vụ khác. Betting là cầu nối giữa người chơi và các tính năng cốt lõi của hệ thống. Đóng vai trò là nguồn dữ liệu chính cho Betting và Risk Management Service. Module này cung cấp cấu trúc và nội dung cho các tùy chọn cá cược, từ đó định hình trải nghiệm người dùng và là cơ sở cho các tính toán rủi ro.
•	Các tính năng chi tiết:
o	Giao diện Cá cược Thể thao: Hiển thị danh sách các môn thể thao, giải đấu, sự kiện đang diễn ra và sắp tới. Cung cấp thông tin chi tiết về trận đấu, đội/vận động viên, và các loại cược khả dụng cùng với tỷ lệ cược tương ứng.
o	Quản lý Tài khoản Người chơi: Cho phép người chơi xem số dư tài khoản, lịch sử nạp/rút tiền, lịch sử đặt cược, và các thông báo liên quan đến tài khoản. Tích hợp với Auth để quản lý thông tin cá nhân.
o	Xử lý Giao dịch Cá cược: Cung cấp quy trình đặt cược đơn giản và nhanh chóng. Người chơi có thể chọn loại cược, nhập số tiền cược, và xác nhận đặt cược. Hệ thống sẽ gửi yêu cầu này đến Risk Management Service để kiểm tra và xử lý. Hệ thống mặc định cho phép bên đặt cược được phép đặt nhiều cửa và nhiều lần trong một sự kiện và nhà cái có quyền tắt tính năng này cho từng loại cược của sự kiện.
o	Hiển thị Kết quả và Thanh toán: Cập nhật kết quả trận đấu theo thời gian thực và tự động thanh toán tiền thắng cược vào tài khoản người chơi. Cung cấp lịch sử kết quả và thống kê chi tiết.
o	Tính năng Tìm kiếm và Lọc: Cho phép người dùng dễ dàng tìm kiếm các sự kiện, đội, hoặc loại cược cụ thể thông qua các bộ lọc theo môn thể thao, giải đấu, thời gian, trạng thái (đang diễn ra, sắp tới, đã kết thúc), và các tiêu chí khác để nhanh chóng tìm thấy thông tin mong muốn.
o	Thông báo Thông minh và Tùy chỉnh: Gửi thông báo cho người dùng về kết quả cược, thay đổi tỷ lệ cược quan trọng, hoặc các chương trình khuyến mãi. Hệ thống sẽ được nâng cấp để cung cấp các cảnh báo thông minh và cá nhân hóa:
	Thông báo Khớp lệnh tiềm năng: Thông báo cho người dùng khi có một phiếu cược được rao bán trên sàn P2P phù hợp với sở thích hoặc lịch sử tìm kiếm của họ.
	Cảnh báo Biến động Giá: Cho phép người dùng theo dõi một phiếu cược cụ thể và nhận cảnh báo khi giá niêm yết của nó thay đổi đáng kể.
	Thông báo Đẩy (Push Notifications): Tích hợp với ứng dụng di động để gửi các thông báo quan trọng trực tiếp đến thiết bị của người dùng.
o	Danh mục Môn thể thao: Quản lý danh sách các môn thể thao được hỗ trợ: American Football, Athletics, Australasian Racing, Australian Rules, Badminton, Bandy, Baseball, Basketball, Beach Volleyball, Bowls, Boxing, Chess, Cricket, Cycling, Darts, Esports, Floorball, Futsal, Gaelic Football, Golf, Handball, Hockey, Horse Racing, Ice Hockey, International Rules, Kabaddi, Lacrosse, MMA, Motor Racing, Motorbikes, Netball, Rowing, Rugby League, Rugby Union, Snooker & Pool, Soccer, Special Markets, Speedway, Surfing, Table Tennis, Tennis, Trotting, Volleyball, Water Polo, Winter Sports, Yachting. Mỗi môn thể thao có thể có các quy tắc và loại cược đặc thù.
o	Quản lý Giải đấu và Sự kiện: Cập nhật thông tin về các giải đấu lớn nhỏ trên toàn thế giới, lịch thi đấu, thông tin đội/vận động viên tham gia, kết quả trận đấu, bảng xếp hạng, và các thống kê liên quan. Dữ liệu này có thể được nhập thủ công hoặc thông qua tích hợp với các API dữ liệu thể thao bên ngoài (ví dụ: các nhà cung cấp dữ liệu tỷ số trực tiếp, kết quả trận đấu, thông tin cầu thủ, thống kê trận đấu, lịch sử đối đầu, tin tức thể thao).
o	Phân Loại và Quy Trình Đặt Cược cho Sự Kiện
Để cung cấp sự linh hoạt cho cả nhà cái và người chơi, hệ thống hỗ trợ hai loại hình tổ chức sự kiện cá cược với quy trình đặt cược khác nhau:
	Sự kiện Cược Tự Do (Variable Stake Event):
	Đây là loại hình cá cược truyền thống và phổ biến nhất.
	Người chơi có thể tự do nhập một số tiền cược bất kỳ mà họ mong muốn, miễn là số tiền đó đáp ứng mức cược tối thiểu (nếu nhà cái có thiết lập).
	Sự kiện Cược Theo Phiếu Cố Định (Fixed Stake Event):
	Đối với loại hình này, nhà cái (người tạo sự kiện) sẽ ấn định một mức cược cố định và duy nhất cho mỗi phiếu tham gia, được gọi là "Giá trị Phiếu cược".
	Tất cả người chơi muốn tham gia sự kiện này đều phải đặt cược đúng bằng Giá trị Phiếu cược đã được định sẵn. Giao diện đặt cược sẽ không có ô nhập số tiền mà thay vào đó là ô nhập số phiếu và nút "Tham gia với giá X VNĐ".
	Mô hình này giúp nhà cái dễ dàng quản lý dòng tiền và tính toán trách nhiệm chi trả.
	Giao diện tạo sự kiện: Trong Admin Panel hoặc giao diện cho nhà cái cá nhân, cần có một lựa chọn để nhà cái quyết định loại hình sự kiện: "Tự do" hay "Theo Phiếu". Nếu chọn "Theo Phiếu", sẽ có một trường để nhập "Giá Trị Phiếu Cược Cố Định".
	Giao diện đặt cược: Trên Betting App, khi người dùng xem một sự kiện "Theo Phiếu", thay vì ô nhập số tiền tự do, họ sẽ chỉ thấy một nút "Mua Phiếu Cược" với mức giá đã được định sẵn.
	Backend Logic: Betting Service và Risk Management Service phải xử lý được cả hai luồng logic này khi người dùng đặt cược.
o	Cấu hình Loại cược: Hệ thống sẽ phân loại và quản lý các loại hình cược dựa trên nguồn dữ liệu đầu vào, bao gồm hai nhóm chính:
	1. Các Loại Cược Được Hỗ Trợ Tự Động (Thông qua API): Đây là những thị trường cược cốt lõi và phổ biến nhất, dữ liệu và tỷ lệ cược sẽ được lấy tự động từ các nhà cung cấp API như API-Sports.io và The-Odds-API.com. Danh sách này sẽ là trọng tâm trong giai đoạn MVP, bao gồm:
	Cược Chính: 
	Thắng-Hòa-Thua (Moneyline / Match Winner 1X2): Cược vào kết quả cuối cùng của trận đấu. 
	Cược Chấp (Point Spread / Asian Handicap): Cược vào một đội với một tỷ lệ chấp điểm/bàn thắng. 
	Cược Tổng số (Totals / Over/Under): Cược vào tổng số điểm/bàn thắng trong trận đấu sẽ cao hơn hay thấp hơn một con số cụ thể. 
	Cơ hội Kép (Double Chance): Cược vào hai trong ba khả năng có thể xảy ra (ví dụ: Đội nhà thắng hoặc hòa).
	Cược Hiệp Đấu: 
	Kết quả Hiệp 1/Cả trận (Half Time/Full Time). Đội thắng Hiệp 1.
	Cược Bàn thắng (chủ yếu cho Bóng đá): 
	Tỷ số chính xác (Correct Score). 
	Cả hai đội ghi bàn (Both Teams to Score). 
	Cược Phụ (Prop Bets - tùy vào sự kiện): 
	Tổng Phạt góc (Corners Over/Under). 
	Tổng Thẻ phạt (Cards Over/Under). 
	Cầu thủ ghi bàn (First/Last Goalscorer). 
	2. Các Loại Cược Mở Rộng (Yêu cầu nhà cái tạo và admin xác minh thủ công): Đây là những loại cược đặc thù, ít phổ biến hơn hoặc không được các API tích hợp trong giai đoạn MVP hỗ trợ. Để các thị trường này xuất hiện, Admin hoặc Super Admin sẽ phải tự tạo sự kiện, thiết lập các cửa cược và tỷ lệ cược ban đầu. Ví dụ: * Player Props, Futures, Each-Way, Forecast/Exacta, Tricast/Trifecta, Cược Hiệp/Nửa trận, Đội Đạt X Điểm Trước, Biên Độ Chiến Thắng, Set Betting, Method of Victory, Round Betting, Fight to Go the Distance, Race Winner, Podium Finish, Head-to-Head, To Make/Miss the Cut, Top Batsman, Top Bowler, Man of the Match, Map Winner, Cược Kèo Đặc Thù Game, Cầu Thủ Xuất Sắc Nhất, Frame Handicap, Highest Break, Highest Checkout.
o	Quy trình Thiết lập Tỷ lệ cược cho Thị trường do Nền tảng Quản lý
Lưu ý quan trọng: Quy trình này chỉ áp dụng cho các sự kiện do Super Admin hoặc Admin của hệ thống tạo ra. Các thị trường do nhà cái cộng đồng (cá nhân/nhóm) tạo sẽ không được cung cấp các công cụ và dữ liệu tham khảo này; họ phải tự thiết lập tỷ lệ cược một cách thủ công. Để giảm thiểu rủi ro và chi phí vận hành, quy trình mở kèo sẽ được phát triển theo lộ trình 3 giai đoạn:
	Giai đoạn 1: Tối ưu hóa Quy trình Thủ công (MVP)
	Xây dựng một "Buồng lái Mở kèo" trong Admin Panel thay vì một form nhập liệu đơn giản. Giao diện này sẽ:
	Hiển thị song song tỷ lệ cược tham khảo từ nhiều nguồn API (ví dụ: The-Odds-API.com).
	Tự động tính toán và điền sẵn tỷ lệ cược gợi ý đã bao gồm biên lợi nhuận (margin) của nền tảng.
	Vai trò của Admin là xem xét, so sánh, điều chỉnh nhỏ nếu cần và nhấn "Phê duyệt" để mở kèo.
	Giai đoạn 2: Bán Tự Động Hóa ("Phê duyệt một chạm")
	Hệ thống tự động tạo ra các "kèo brouillon" (draft markets) với tỷ lệ cược đã được đề xuất cho tất cả các sự kiện sắp tới.
	Giao diện của Admin trở thành một danh sách các kèo đang chờ duyệt. Vai trò của họ được rút gọn thành việc kiểm tra và "Phê duyệt hàng loạt", chỉ can thiệp sâu vào các kèo có cảnh báo chênh lệch dữ liệu lớn.
	Giai đoạn 3: Tự Động Hóa Hoàn Toàn (Tầm nhìn dài hạn)
	Hệ thống sẽ tự động mở kèo cho các giải đấu lớn và đáng tin cậy dựa trên một "Điểm Tin Cậy" (Confidence Score) được tính toán từ sự tương đồng của các nguồn API.
	Vai trò của Admin lúc này là giám sát và xử lý các trường hợp ngoại lệ mà hệ thống không đủ tự tin để tự động quyết định.
o	Cập nhật Dữ liệu liên tục: Đảm bảo dữ liệu về các sự kiện, tỷ số, và thông tin liên quan được cập nhật theo thời gian thực, phục vụ cho việc hiển thị trên Betting và tính toán rủi ro.
o	Tính năng Chuyển Giao Rủi Ro (Cash Out & Marketplace)
Đây chính là phần cốt lõi và phức tạp mà bạn muốn cân nhắc: cho phép người nắm giữ phiếu cược bán lại nó cho một người chơi khác. Trong ngành cá cược, tính năng này có hai hình thức phổ biến: "Cash Out" (Rút tiền sớm) và "Betting Exchange" (Sàn giao dịch cá cược). Ý tưởng là sự kết hợp của cả hai, nghiêng về phía tạo ra một thị trường thứ cấp. Để nâng cao trải nghiệm và cung cấp cho người chơi sự kiểm soát lớn hơn đối với các cược đang hoạt động của mình, hệ thống sẽ phát triển tính năng cho phép người chơi thoát khỏi một vị thế cược trước khi sự kiện kết thúc. 
A. Phương Án 1: "Cash Out" do Nền tảng điều khiển (Chi tiết hóa)
1. Mô tả: Đây là tính năng cho phép người chơi bán lại phiếu cược đang hoạt động của mình cho chính nhà cái (người đã tạo ra sự kiện đó) trước khi sự kiện kết thúc. Giá trị mua lại sẽ được tính toán động dựa trên diễn biến thực tế của trận đấu.
2. Công Thức Tính Toán Chi Tiết: Giá trị Cash Out được tính dựa trên nguyên tắc "giá trị công bằng" (fair value) của phiếu cược tại thời điểm yêu cầu, sau đó trừ đi một khoản phí cho nền tảng.
•	Giá trị Công bằng (Fair Value): Là giá trị lý thuyết của phiếu cược nếu nó được tạo ra với tỷ lệ cược trực tiếp (live odds).
Giá trị công bằng = Tiền thưởng chiến thắng tiềm năng ban đầu × 1 / Tỷ lệ cược trực tiếp
Hoặc một công thức tương đương và dễ hiểu hơn:
Giá trị công bằng = Tiền cược gốc × Tỷ lệ cược gốc / Tỷ lệ cược trực tiếp
•	Giá trị Cash Out cuối cùng:
Giá trị Cash Out cuối cùng = Giá trị Công Bằng × (1 − Phí Cash Out)
o	Tỷ lệ cược gốc (Original Odds): Tỷ lệ tại thời điểm người chơi đặt cược.
o	Tỷ lệ cược trực tiếp (Live Odds): Tỷ lệ của chính cửa cược đó tại thời điểm yêu cầu Cash Out, do Risk Management Service cung cấp.
o	Phí Cash Out (Cash Out Fee/Margin): Một tỷ lệ phần trăm do nhà cái (Admin hệ thống hoặc nhà cái cộng đồng) thiết lập để đảm bảo lợi nhuận từ việc cung cấp tính năng này.
Ví dụ:
•	Người chơi đặt cược 100,000 VNĐ vào cửa A với tỷ lệ cược gốc là 3.0. Tiền thắng tiềm năng là 300,000 VNĐ.
•	Trong trận, đội A dẫn trước. Tỷ lệ cược trực tiếp của cửa A giảm xuống còn 1.5.
•	Giá trị Công bằng = 100,000 * (3.0 / 1.5) = 200,000 VNĐ.
•	Giả sử Phí Cash Out là 5% (0.05).
•	Giá trị Cash Out đề xuất = 200,000 * (1 - 0.05) = 190,000 VNĐ.
3. Quy Trình Vận Hành và Tương Tác Giữa Các Service: Luồng xử lý Cash Out sẽ yêu cầu sự phối hợp chặt chẽ giữa các service, áp dụng 
Saga Pattern để đảm bảo tính nhất quán của dữ liệu.
•	Bước 1: Yêu cầu giá (Betting App → Betting Service)
o	Người chơi nhấn nút "Cash Out" trên một phiếu cược đang hoạt động trong Betting App.
o	Betting Service nhận yêu cầu, chứa ID của phiếu cược gốc.
•	Bước 2: Lấy Tỷ Lệ Cược Trực Tiếp (Betting Service → Risk Management Service)
o	Betting Service gửi yêu cầu đến Risk Management Service để lấy tỷ lệ cược trực tiếp (live odds) mới nhất cho cửa cược tương ứng. 
•	Bước 3: Tính Toán và Hiển Thị Đề Xuất (Betting Service → Betting App)
o	Risk Management Service trả về tỷ lệ cược trực tiếp.
o	Betting Service thực hiện tính toán "Giá trị Cash Out" theo công thức trên.
o	Giá trị này được gửi về Betting App và hiển thị cho người chơi, kèm theo một bộ đếm thời gian (ví dụ: 10 giây) để giá trị hết hạn, do tỷ lệ cược thay đổi liên tục.
•	Bước 4: Xác nhận Giao Dịch (Betting App → Betting Service)
o	Người chơi xác nhận đồng ý với giá trị Cash Out.
•	Bước 5: Thực Thi Saga Giao Dịch (Phối hợp giữa các Service)
o	Một Saga được khởi tạo để đảm bảo giao dịch diễn ra một cách an toàn.
o	Betting Service: Phát ra sự kiện CashoutRequested. Cập nhật trạng thái phiếu cược thành CASHING_OUT.
o	Wallet Service: Lắng nghe sự kiện CashoutRequested. Thực hiện giao dịch cộng "Giá trị Cash Out" vào ví người dùng. Nếu thành công, phát ra sự kiện CashoutFundsCredited. Nếu thất bại, phát ra CashoutFailed.
o	Betting Service (Hoàn tất/Bù trừ):
	Lắng nghe CashoutFundsCredited: Cập nhật trạng thái phiếu cược thành CASHED_OUT (đã thanh toán).
	Lắng nghe CashoutFailed: Thực hiện giao dịch bù trừ, chuyển trạng thái phiếu cược về lại ACTIVE (đang hoạt động).
o	Risk Management Service: Lắng nghe sự kiện CashoutFundsCredited. Thực hiện hành động quan trọng:
	Xóa bỏ trách nhiệm chi trả (Liability) của phiếu cược gốc. Vì phiếu cược này đã được thanh toán, nó không còn là một rủi ro tiềm tàng nữa.
	Ghi nhận khoản tiền Cash Out như một giao dịch đã thanh toán, ảnh hưởng đến P&L (Lãi và Lỗ) của sự kiện.
4. Quy Tắc Nghiệp Vụ và Cấu Hình:
•	Quyền Bật/Tắt: Như đã nêu trong tài liệu, nhà cái (Admin hệ thống hoặc nhà cái cộng đồng) có quyền bật hoặc tắt tính năng "Cash Out" cho từng sự kiện/thị trường khi tạo.
•	Các trường hợp không khả dụng: Nút "Cash Out" sẽ tự động bị vô hiệu hóa khi:
o	Một sự kiện quan trọng vừa xảy ra (ví dụ: có bàn thắng, thẻ đỏ, VAR) và thị trường bị tạm khóa.
o	Risk Management Service không thể cung cấp tỷ lệ cược trực tiếp đáng tin cậy.
o	Cửa cược của người chơi đã thua (ví dụ: cược Tài 2.5 và trận đấu đã có 3 bàn).
•	Cấu hình Phí: 
o	Phí Cash Out phải là một tham số có thể cấu hình trong Admin Panel cho từng nhà cái.
o	Nếu Cash Out trước khi trận đâu diễn ra thì sẽ không bị mất phí cash out và bên đặc cược sẽ chỉ được hoàn lại số tiền gốc bỏ ra đặc cược vào ví, còn khoản thưởng chiến thắng tiềm năng sẽ không được tính vào.
o	Phí cash out của nhà cái của hệ thống là Super admin hay admin do super admin của hệ thống chỉ định sẽ luôn được thiết lập ở mức khởi đầu tối thiểu tương đương mức lợi nhuân Margin được thiết lập cho sự kiện.
o	Phí cash out của nhà cái là người dùng cá nhân hoặc nhóm người dùng sẽ mặc định được thiết lập khởi đầu ở mức tối thiểu là 0%.
•	Cash Out cho Cược Xâu (Parlay):
o	Công thức vẫn được áp dụng.
o	Tỷ lệ cược gốc là tỷ lệ tổng của cược xâu.
o	Tỷ lệ cược trực tiếp được tính bằng cách nhân tỷ lệ của các cửa đã thắng với tỷ lệ cược trực tiếp (live odds) của các cửa chưa diễn ra. Các cửa đã thua sẽ khiến phiếu cược không thể Cash Out.
•	Quy tắc Đặc biệt: Cash Out Trước Khi Trận Đấu Bắt Đầu:
o	Cơ chế hoạt động: Đối với các sự kiện cho phép, người chơi có thể thực hiện Cash Out trước giờ trận đấu chính thức bắt đầu. Trong trường hợp này, người chơi sẽ nhận lại đúng số tiền cược gốc đã bỏ ra, không phát sinh lãi/lỗ và không bị tính phí.
o	Tính năng Tùy chọn: Đây là một tính năng có thể được nhà cái bật hoặc tắt cho từng sự kiện.
o	Mặc định và Chiến lược: Để khuyến khích sự phát triển và tăng tính thanh khoản cho Sàn Giao Dịch P2P, tính năng "Cash Out trước trận" sẽ được tắt ở trạng thái mặc định. Điều này định hướng người dùng muốn thoát vị thế sớm hãy niêm yết phiếu cược của mình lên sàn P2P để tìm kiếm một thỏa thuận với người chơi khác.
B. Phương Án 2: Sàn Giao Dịch Phiếu Cược Ngang Hàng (P2P Marketplace)
1. Mô tả
Đây là một tính năng cao cấp, biến nền tảng thành một sàn giao dịch thực thụ, nơi người chơi có thể mua bán, trao đổi các phiếu cược đang hoạt động với nhau. Phương án này được thiết kế cho những người chơi chuyên nghiệp hơn. Nó cho phép người bán có thể đặt một mức giá cao hơn so với giá "Cash Out" mà nhà cái đề nghị và chờ một người chơi khác mua lại. Đồng thời, họ cũng có thể giao dịch các phiếu cược mà nhà cái không bật tính năng "Cash Out". Hành động này có tiềm năng mang lại lợi nhuận cao hơn nhưng không đảm bảo giao dịch sẽ thành công.
Mục tiêu chính:
•	Tạo ra một thị trường thứ cấp sôi động: Cho phép người chơi giao dịch các vị thế cược của mình, tạo ra một lớp tương tác và chiến lược mới.
•	Tối đa hóa lợi nhuận cho người chơi: Người bán có thể đặt giá bán cao hơn so với giá "Cash Out" của nhà cái, trong khi người mua có cơ hội tiếp cận các vị thế cược tiềm năng mà không cần đặt cược từ đầu.
•	Giải quyết vấn đề thanh khoản: Thông qua tính năng bán cược phân mảnh, hệ thống giúp các phiếu cược có giá trị lớn vẫn có thể được giao dịch dễ dàng.
•	Tăng sự gắn kết và tương tác: Biến nền tảng từ một nơi đặt cược đơn thuần thành một cộng đồng tài chính, nơi người dùng có thể phân tích và giao dịch giá trị.
2. Cách hoạt động
Người chơi có thể rao bán phiếu cược của mình với một mức giá do họ tự đặt. Một người chơi khác nếu thấy hợp lý có thể mua lại. Trong mô hình này, nền tảng sẽ đóng vai trò trung gian và không thu bất kỳ một khoản phí hoa hồng nào trên mỗi giao dịch thành công.
Một điểm cốt lõi là đối với nhà cái ban đầu (người phát hành phiếu cược), trách nhiệm chi trả của họ không thay đổi. Hệ thống chỉ quan tâm ai là người nắm giữ phiếu cược cuối cùng để trả thưởng khi sự kiện kết thúc.
3. Tác Động Về Mặt Kỹ Thuật
Việc xây dựng một Sàn Giao Dịch (Marketplace) là yêu cầu bắt buộc, không còn là nơi người chơi chỉ cược với nhà cái. "Chợ" này phải có các chức năng:
•	Người bán có thể "đăng bán" phiếu cược của mình với giá mong muốn trước khi sự kiện kết thúc.
•	Người mua có thể xem danh sách các phiếu cược đang được bán và chọn mua trước khi sự kiện kết thúc.
•	Cần có một cơ chế khớp lệnh (matching engine) khi hai bên đồng ý giá.
o	Cần xây dựng một cơ chế khớp lệnh có khả năng xử lý các loại lệnh phức tạp.
o	Hệ thống phải xử lý được cả lệnh "khớp toàn bộ" (fill or kill) và "khớp một phần" (partial fill) để phục vụ cho tính năng bán cược phân mảnh.
•	Quy tắc Giao dịch Phần sở hữu (Ownership Share Trading Rules):
o	Quyền Rao Bán Lại: Một người dùng sở hữu một phần của phiếu cược (ví dụ: 10%) có toàn quyền rao bán lại phần sở hữu đó của mình trên Sàn Giao Dịch P2P.
o	Nguyên tắc Không Phân Mảnh Thêm: Phần sở hữu được rao bán lại không được phép phân mảnh thêm nữa. Người mua phải mua toàn bộ phần sở hữu đang được rao bán. Ví dụ, nếu người dùng B sở hữu 10% và muốn bán, họ phải bán toàn bộ 10% đó cho người dùng E, chứ không thể chia nhỏ thành hai phần 5% để bán.
•	Hệ thống phải quản lý các trạng thái phức tạp hơn cho phiếu cược, không chỉ là "Đã đặt" -> "Thắng/Thua", mà còn có thêm các trạng thái như: "Đang rao bán", "Đã chuyển nhượng".
•	Thay đổi Mô hình Dữ liệu (Quan trọng nhất):
o	Quyền sở hữu phiếu cược phải được thiết kế lại. Thay vì một trường owner_id duy nhất, hệ thống cần một bảng quan hệ mới, ví dụ: BetSlip_Ownership, để theo dõi quyền sở hữu của nhiều người trên cùng một phiếu cược một cách an toàn và chắc chắn.
o	Bảng BetSlip_Ownership:
	id: Khóa chính.
	bet_slip_id: Khóa ngoại, liên kết đến phiếu cược gốc.
	owner_id: Khóa ngoại, liên kết đến người dùng sở hữu.
	ownership_percentage: Tỷ lệ sở hữu (ví dụ: 100.0, 90.0, 10.0).
o	Điều này giúp giải quyết bài toán quản lý trạng thái phức tạp khi quyền sở hữu được chuyển nhượng.
•	Luồng Thanh Toán Phân tán (Distributed Payout Flow):
o	Khi phiếu cược thắng, Betting Service phải được nâng cấp để đọc dữ liệu từ bảng BetSlip_Ownership.
o	Dựa trên tỷ lệ sở hữu, Betting Service sẽ tính toán và gửi nhiều yêu cầu thanh toán riêng lẻ đến Wallet Service để cộng tiền thưởng cho tất cả các chủ sở hữu một cách chính xác.
•	Đồng Bộ Hóa Thời Gian Thực, Tạm Khóa Thị Trường và Cơ chế Khớp lệnh theo Phiên:
o	Để đảm bảo tính công bằng và ngăn chặn lợi thế từ tốc độ kết nối (front-running) tránh tình trạng người mua lợi dụng độ trễ thông tin để mua phiếu cược với giá hời, hệ thống sẽ áp dụng hai cơ chế bảo vệ:
o	1.  Tạm khóa Thị trường (Market Suspension): Khi có một sự kiện quan trọng trong trận đấu (bàn thắng, thẻ đỏ, penalty), Sports Data Service sẽ phát ra một sự kiện. Sàn Giao Dịch P2P sẽ ngay lập tức tạm khóa (suspend) tất cả các lệnh rao bán liên quan đến trận đấu đó.
o	2. Cơ chế Khớp lệnh theo Phiên (Session-based Matching): Khi thị trường được mở lại sau khi tạm khóa, hệ thống sẽ kích hoạt một "phiên khớp lệnh" ngắn để đảm bảo công bằng, bao gồm: 
	Giai đoạn Thu thập lệnh (10-15 giây): Trong khoảng thời gian này, tất cả các lệnh mua và bán mới được người dùng đặt sẽ được hệ thống thu thập và giữ lại trong hàng chờ, chưa thực hiện khớp lệnh ngay lập tức.
	Giai đoạn Khớp lệnh đồng thời (5-10 giây): Ngay khi kết thúc phiên, Matching Engine sẽ xử lý tất cả các lệnh trong hàng chờ cùng một lúc. Các lệnh sẽ được ưu tiên khớp dựa trên giá tốt nhất trước, sau đó mới đến thời gian đặt lệnh. Cơ chế này loại bỏ lợi thế của người đặt lệnh nhanh nhất, nhưng vẫn tôn trọng mức giá mà người dùng tự do đưa ra.
4. Vai trò của Nền tảng và Mô hình Doanh thu
•	Vai trò Trung gian: Nền tảng chỉ đóng vai trò là một trung gian, cung cấp công nghệ và một môi trường an toàn để người dùng giao dịch với nhau. Do tất cả giao dịch đều diễn ra trên ví nội bộ của hệ thống sau khi người dùng đã nạp tiền, sẽ không phát sinh thêm chi phí từ Cổng Thanh Toán bên ngoài cho các giao dịch P2P này.
•	Mô hình Doanh thu: 
o	Giai đoạn đầu: Nền tảng sẽ không thu phí hoa hồng để khuyến khích người dùng.
o	Lộ trình tương lai: Khi thị trường đã phát triển, hệ thống có thể cân nhắc áp dụng một khoản phí giao dịch nhỏ, được chia đều cho cả người mua và người bán. Mô hình này đảm bảo sự công bằng và duy trì chi phí thấp cho người dùng. Trong tương lai, việc thu một khoản phí nhỏ (ví dụ: 1-2% trên giá trị giao dịch) có thể được cân nhắc như một nguồn doanh thu mới và khoản phí này có thể được điều chỉnh chỉ bởi Super Admin tại giao diện của họ và mỗi khi có thay đổi thì toàn bộ người dùng sẽ nhận được email thông báo và 1 nút xác nhân.
•	Minh Bạch Hóa Phí Giao Dịch:
o	Để đảm một môi trường giao dịch cực kỳ linh hoạt, công bằng và minh bạch, mô phỏng theo các sàn giao dịch tài chính chuyên nghiệp, giao diện xác nhận giao dịch P2P phải hiển thị rõ ràng cấu trúc phí trước khi người dùng hoàn tất.
o	Ví dụ: Nếu người bán niêm yết giá 120,000 VNĐ và phí giao dịch là 1% cho mỗi bên:
	Giao diện của Người mua sẽ hiển thị:
	Giá trị phiếu cược: 120,000 VNĐ
	Phí giao dịch (1%): + 1,200 VNĐ
	Tổng số tiền bạn trả: 121,200 VNĐ
	Giao diện của Người bán sẽ hiển thị:
	Giá trị bán: 120,000 VNĐ
	Phí giao dịch (1%): - 1,200 VNĐ
	Tổng số tiền bạn nhận: 118,800 VNĐ
5. Quan Hệ với Nhà Cái Gốc
•	Trách nhiệm không đổi: Điều quan trọng cần nhấn mạnh là Sàn Giao Dịch P2P không làm thay đổi trách nhiệm chi trả của nhà cái gốc (người phát hành phiếu cược ban đầu).
•	Nghĩa vụ của nhà cái gốc chỉ là thanh toán đúng số tiền thắng tiềm năng cho phiếu cược đó khi sự kiện kết thúc. Hệ thống sẽ tự động điều phối khoản tiền đó đến (những) người chủ sở hữu cuối cùng của phiếu cược. Nhà cái gốc không tham gia và không bị ảnh hưởng bởi các hoạt động mua bán trên thị trường thứ cấp.
6. Tác Động Về Mặt Trải Nghiệm Người Dùng (UX)
Giao diện sẽ trở nên phức tạp hơn đáng kể. Người dùng cần hiểu rõ các thông số như giá trị cược gốc, tỷ lệ cược gốc, lợi nhuận tiềm năng, giá đang rao bán, và tỷ lệ cược trực tiếp của trận đấu để ra quyết định. Đây là một tính năng được xác định dành cho người dùng chuyên nghiệp.
7. Giải Pháp Cho Vấn Đề Thanh Khoản: "Phân Mảnh" Phiếu Cược và Giao Dịch Phần sở hữu (Fractional Ownership & Secondary Market Syndication)
Để giải quyết vấn đề các phiếu cược giá trị cao khó tìm người mua duy nhất, hệ thống sẽ triển khai tính năng Phân mảnh Phiếu cược. Tính năng này cho phép một phiếu cược được sở hữu chung bởi nhiều người, giúp tăng thanh khoản và khả năng tiếp cận.
•	Cơ Chế Hoạt Động: Khi rao bán phiếu cược trên Sàn Giao Dịch P2P, người bán sẽ có tùy chọn "Phân Mảnh và Bán Phần sở hữu". Họ sẽ thiết lập tổng giá bán mong muốn và số lượng "phần sở hữu" muốn tạo. Hệ thống sẽ tự động tính ra giá của mỗi phần sở hữu.
•	Luồng Hoạt Động Của Người Bán:
o	Trong mục "Cược của tôi", người bán chọn một phiếu cược đang hoạt động và nhấn "Rao bán trên Marketplace". 
o	Hệ thống hiển thị giá trị "Cash Out" hiện tại từ nhà cái nếu có, nếu không có thì có thể mượn từ nhà cái hệ thống là super admin hoặc admin do super admin chỉ định để người bán tham khảo nếu có.
o	Nhập tổng giá trị muốn bán (ví dụ: 120,000 VNĐ).
o	Người bán sẽ có một tùy chọn cốt lõi: "Cho phép bán từng phần (bán phân mảnh)". Nhập số lượng phần sở hữu muốn tạo (ví dụ: 10 phần sở hữu).
o	Hệ thống hiển thị: "Giá tham khảo của mỗi phần sở hữu là 12,000 VNĐ".
o	Sau khi xác nhận, phiếu cược sẽ được niêm yết trên Sàn Giao Dịch. Người bán có thể theo dõi trạng thái lệnh bán của mình và Hủy lệnh Bán: Người bán có toàn quyền hủy lệnh niêm yết của mình bất cứ lúc nào đối với phần phiếu cược chưa được bán. Tính Bất biến của Giao dịch Đã Thành Công: Khi một phần của phiếu cược đã được bán thành công cho người mua khác, giao dịch đó là cuối cùng và không thể đảo ngược. Quyền sở hữu đối với các phần đã bán sẽ không bị ảnh hưởng bởi việc người bán hủy lệnh niêm yết đối với phần còn lại. Người bán chỉ lấy lại quyền kiểm soát đối với phần trăm sở hữu mà họ chưa bán được.
•	Luồng Hoạt Động Của Người Mua:
o	Người mua truy cập vào Sàn Giao Dịch (Marketplace) và thấy danh sách các phiếu cược đang được rao bán.
o	Họ có thể lọc và tìm kiếm dựa trên nhiều tiêu chí (môn thể thao, trận đấu, giá bán, ...).
o	Khi chọn một phiếu cược, giao diện sẽ hiển thị đầy đủ thông tin: cược gốc, tỷ lệ cược gốc, tiền thắng tiềm năng, giá bán do người bán đặt ra, số phần sở hữu còn lại.
o	Nếu phiếu cược đó cho phép bán phân mảnh:
	Người mua sẽ thấy một ô để nhập "Số phần sở hữu muốn mua" và "Mức giá mong muốn giao dịch chi trả".
	Hệ thống sẽ xử lý theo một trong hai kịch bản:
	Kịch bản 1: Khớp lệnh Tự động (Giá mua ≥ Giá bán): Nếu người mua trả giá bằng hoặc cao hơn giá người bán đang niêm yết, giao dịch cho phần đó sẽ được khớp lệnh ngay lập tức và tự động.
	Kịch bản 2: Chào Mua/Trả giá (Giá mua < Giá bán): Nếu người mua trả một mức giá thấp hơn, yêu cầu của họ sẽ không bị hủy. Thay vào đó, nó sẽ trở thành một "lệnh chào mua" (bid). Hệ thống sẽ gửi một thông báo đến người bán với nội dung: "Người dùng X muốn mua một phần trị giá Y VNĐ với giá Z VNĐ. Bạn có đồng ý không?".
	Hệ thống sẽ tự động tính và hiển thị tỷ lệ sở hữu và lợi nhuận tiềm năng tương ứng với số tiền đó.
	Ví dụ: "Với 12,000 VNĐ, bạn sẽ sở hữu 10% phiếu cược và nhận 10% tiền thưởng nếu thắng."
o	Nếu phiếu cược không cho phép bán phân mảnh, người mua chỉ có một lựa chọn duy nhất là "Mua toàn bộ".
o	Xác nhận giao dịch.
•	Quản lý Chào Mua (Đối với Người Bán):
Người bán sẽ có một giao diện để quản lý tất cả các "lệnh chào mua" đang chờ xử lý cho phiếu cược của mình.
Tại đây, họ có hai lựa chọn cho mỗi lệnh chào mua: "Chấp nhận" hoặc "Từ chối". Nếu chấp nhận, giao dịch sẽ được thực thi ngay lập tức.
•	Ràng buộc Kỹ thuật về Phân Mảnh:
Để đảm bảo mọi phép tính chia tỷ lệ sở hữu luôn ra số thập phân hữu hạn (tránh các số vô hạn tuần hoàn như 1/3 = 0.333...), tổng số tiền cược gốc của một phiếu cược khi được tạo phải tuân thủ quy tắc chia hết cho 2^n * 5^m (với n, m là số tự nhiên). Điều này có nghĩa là các mẫu số như 2, 5, 10, 20, 25, 40, 50, 80, 100... là hợp lệ, giúp hệ thống tránh được các lỗi làm tròn và đảm bảo tính chính xác tuyệt đối khi phân chia lợi nhuận. Ngoài ra, hệ thống sẽ áp dụng các quy tắc sau: 
o	Xử lý phần dư (Remainder Handling): Mọi phần dư phát sinh trong quá trình tính toán sẽ được hệ thống ghi nhận và xử lý theo quy tắc được định sẵn để đảm bảo không thất thoát. 
o	Xác thực tổng sở hữu: Sau mỗi giao dịch mua/bán một phần phiếu cược, hệ thống sẽ thực hiện một bước kiểm tra để đảm bảo tổng tỷ lệ sở hữu của tất cả các bên trên phiếu cược đó luôn bằng chính xác 100%.
•	Xử Lý của Hệ Thống:
o	Quản lý Sở hữu: Hệ thống sẽ sử dụng một bảng dữ liệu riêng để theo dõi quyền sở hữu của từng phần sở hữu, liên kết ID phiếu cược với ID của người dùng và số phần sở hữu họ nắm giữ.
o	Xử lý Bán Không Hết: Nếu phiếu cược không bán hết tất cả các phần sở hữu trước khi sự kiện kết thúc, người bán ban đầu sẽ tiếp tục sở hữu các phần sở hữu chưa bán được.
o	Phân Chia Lợi Nhuận Tự Động: Khi phiếu cược thắng, hệ thống sẽ tự động tính toán tổng tiền thưởng và phân chia cho tất cả các chủ sở hữu phần sở hữu theo đúng tỷ lệ họ nắm giữ. Khoản tiền này sẽ được cộng trực tiếp vào ví của từng người.
C. Phương Án 3: Tự Động Hóa Quản Lý Vị Thế (Chốt Lời & Cắt Lỗ)
1. Tổng Quan Chức Năng
Để nâng cao khả năng quản lý rủi ro và tối ưu hóa lợi nhuận cho người chơi, hệ thống sẽ tích hợp thêm tính năng Chốt Lời (Take Profit) và Cắt Lỗ (Stop Loss) tự động. Chức năng này hoạt động như một lớp tự động hóa dựa trên nền tảng của tính năng "Cash Out", cho phép người dùng đặt trước các lệnh để hệ thống tự động thực thi khi giá trị phiếu cược đạt đến ngưỡng mong muốn.
•	Chốt Lời (Take Profit): Tự động thực hiện "Cash Out" khi giá trị phiếu cược đạt hoặc vượt một mức lợi nhuận mục tiêu do người chơi thiết lập.
•	Cắt Lỗ (Stop Loss): Tự động thực hiện "Cash Out" khi giá trị phiếu cược giảm xuống bằng hoặc thấp hơn một ngưỡng thua lỗ tối đa mà người chơi có thể chấp nhận.
Tính năng này giúp người chơi quản lý vị thế một cách kỷ luật mà không cần phải theo dõi diễn biến trận đấu liên tục.
Lưu ý quan trọng là tính năng này chỉ có thể được áp dụng nếu như sự kiện được nhà cái thiết lập cho phép cash-out. Bên cạnh đó vì để phât triển thị trường p2p marketplace thì tính năng này mặc định là tắt chưa kích hoạt, chỉ bật khi người dùng có nhu cầu mong muốn sử dụng.
2. Luồng Hoạt Động Của Người Dùng
•	Thiết Lập Lệnh: Trong mục quản lý các phiếu cược đang hoạt động, bên cạnh nút "Cash Out" thủ công, người dùng sẽ có tùy chọn "Thiết Lập Lệnh Tự Động".
•	Nhập Ngưỡng: Giao diện cho phép người dùng nhập hai giá trị: giá trị chốt lời và giá trị cắt lỗ.
•	Xác Nhận và Theo Dõi: Sau khi xác nhận, phiếu cược sẽ có chỉ báo trực quan cho thấy lệnh tự động đang hoạt động. Người dùng có thể hủy các lệnh này bất cứ lúc nào trước khi chúng được kích hoạt.
3. Yêu Cầu Kỹ Thuật và Tương Tác Giữa Các Service
•	Tầng Data: Bảng dữ liệu phiếu cược trong Transaction Database sẽ được mở rộng với các trường take_profit_threshold, stop_loss_threshold, và auto_order_status.
•	Tầng Business Logic:
o	Một service nền mới (AutoCashoutMonitorService) sẽ được triển khai. Service này hoạt động theo chu kỳ (ví dụ: mỗi 5-10 giây) để quét các phiếu cược có lệnh tự động đang hoạt động.
o	Đối với mỗi phiếu cược, service sẽ gọi đến 
Betting Service để tính toán giá trị "Cash Out" hiện tại, quá trình này yêu cầu Betting Service phải lấy tỷ lệ cược trực tiếp từ Risk Management Service.
o	Nếu giá trị "Cash Out" hiện tại chạm một trong các ngưỡng đã đặt, 
AutoCashoutMonitorService sẽ khởi tạo quy trình Saga Giao Dịch Cash Out y hệt như luồng xử lý thủ công, bắt đầu bằng việc yêu cầu Betting Service phát ra sự kiện CashoutRequested.
•	Quy Tắc Nghiệp Vụ: Các lệnh tự động sẽ bị tạm dừng khi thị trường bị nhà cái khóa và sẽ hoạt động trở lại khi thị trường mở. Người dùng sẽ nhận được thông báo khi một lệnh được thực thi thành công.
•	Lưu ý cho Giai đoạn MVP: Chiến lược triển khai thị trường cược 
Danh sách các môn thể thao và loại cược được liệt kê trong tài liệu đại diện cho tầm nhìn dài hạn và khả năng mở rộng tối đa của nền tảng. Trong Giai đoạn 1 (MVP), để tối ưu hóa nguồn lực và đảm bảo tính ổn định, hệ thống sẽ áp dụng một chiến lược kết hợp thông minh:
1. Triển khai các thị trường được API hỗ trợ: Hệ thống sẽ ưu tiên triển khai các môn thể thao và loại cược được hỗ trợ tự động bởi hai nhà cung cấp API đã chọn là The Odds API và API-Sports.io. 
2. Áp dụng quy trình quản lý thủ công: Đối với bất kỳ môn thể thao hoặc loại cược nào nằm trong tầm nhìn dài hạn nhưng không được hai API trên hỗ trợ, hệ thống sẽ cho phép Admin/Super Admin tạo và quản lý các thị trường này theo cách thủ công. Admin sẽ chịu trách nhiệm thiết lập sự kiện, các cửa cược và tỷ lệ cược ban đầu. Chiến lược này cho phép nền tảng vừa có thể cung cấp nhanh chóng các thị trường phổ biến một cách tự động, vừa có sự linh hoạt để cung cấp các thị trường độc đáo, phục vụ các nhóm người chơi chuyên biệt. Danh sách các thị trường sẽ được mở rộng trong tương lai khi tích hợp thêm các nhà cung cấp dữ liệu cao cấp hơn. 

Module Quản Lý Rủi Ro Nhà Cái
•	Chức năng chính: Module Quản Lý Rủi Ro là thành phần quan trọng nhất, chịu trách nhiệm bảo vệ lợi nhuận và sự ổn định tài chính của nhà cái. Nó chuyển đổi hoạt động cá cược từ một trò chơi may rủi thành một bài toán quản trị rủi ro tài chính được kiểm soát chặt chẽ.
•	Vai trò trong hệ thống: Đây là bộ não của hệ thống, phân tích dữ liệu từ các module khác để đưa ra các quyết định quan trọng về tỷ lệ cược và chấp nhận rủi ro. Nó tương tác với Betting để cung cấp tỷ lệ cược và với Auth để áp dụng các chính sách rủi ro khác nhau cho từng loại nhà cái.
•	Các tính năng chi tiết:
o	Quản lý Trách nhiệm Chi trả (Liability Management): Tính toán và theo dõi liên tục tổng số tiền mà nhà cái có thể phải trả cho mỗi kết quả có thể xảy ra của một sự kiện. Đây là chỉ số cốt lõi để đánh giá mức độ rủi ro.
o	Trụ cột 2: Hệ thống Tự động Điều chỉnh Tỷ lệ cược Linh hoạt (Dynamic Odds):
	Tự động điều chỉnh tỷ lệ cược theo thời gian thực dựa trên dòng tiền đặt cược cũng như thời gian thi đấu còn lại nếu có. Khi tiền đổ dồn vào một cửa, hệ thống sẽ hạ tỷ lệ cược của cửa đó và tăng tỷ lệ của các cửa khác để cân bằng lại rủi ro và khuyến khích người chơi đặt cược vào các lựa chọn khác.
	Phạm vi áp dụng và Nguyên tắc cốt lõi: Cơ chế "Dynamic Odds" của hệ thống được thiết kế để hoạt động hoàn toàn độc lập với thị trường bên ngoài. Nhiệm vụ duy nhất của nó là cân bằng rủi ro nội bộ của nền tảng. Hệ thống sẽ chỉ điều chỉnh tỷ lệ cược dựa trên duy nhất một yếu tố: dòng tiền mà người dùng đặt vào các cửa trên chính nền tảng. Mục tiêu là để đảm bảo sổ cược của nhà cái (chính là nền tảng) được cân bằng và Trách nhiệm Chi trả (Liability) luôn nằm trong Ngưỡng Rủi Ro Tối Đa đã thiết lập. Hệ thống sẽ không tự động điều chỉnh tỷ lệ cược theo biến động từ các nhà cái khác trên thế giới. Việc này đảm bảo tính tự chủ và giúp nhà cái quản lý rủi ro dựa trên tình hình kinh doanh thực tế của mình.
o	Thiết lập Biên lợi nhuận Nhà cái (Vigorish/Margin): Cho phép nhà cái thiết lập một biên lợi nhuận mong muốn, đảm bảo rằng ngay cả khi sổ cược cân bằng, nhà cái vẫn có lợi nhuận lý thuyết. Hệ thống sẽ tính toán tỷ lệ cược sao cho tổng xác suất nghịch đảo của chúng luôn lớn hơn 100%.
o	Ngưỡng Rủi ro Tối đa và Khóa Thị trường Tự động: Cho phép nhà cái đặt ra một mức lỗ tối đa có thể chấp nhận cho mỗi lựa chọn hoặc sự kiện. Nếu một giao dịch đặt cược có nguy cơ khiến trách nhiệm chi trả vượt qua ngưỡng này, hệ thống sẽ tự động từ chối giao dịch đó và có thể tạm thời khóa việc nhận cược cho lựa chọn đó (phanh khẩn cấp).
o	Quản lý Rủi ro cho Khuyến mãi: Áp dụng các ngưỡng rủi ro riêng biệt và nghiêm ngặt hơn cho các chương trình khuyến mãi (ví dụ: tăng tỷ lệ, cược miễn phí) để kiểm soát chi phí và ngăn chặn lạm dụng.
o	Báo cáo và Phân tích Rủi ro: Cung cấp các báo cáo chi tiết về dòng tiền, trách nhiệm chi trả, lợi nhuận và các chỉ số rủi ro khác, giúp nhà cái có cái nhìn tổng quan và đưa ra các quyết định chiến lược.
Module Dữ Liệu Thể Thao (Sports Data Service) - Trung gian Độc lập
•	Chức năng chính: 
o	Đây là module chịu trách nhiệm là nguồn cung cấp dữ liệu duy nhất và đáng tin cậy (Single Source of Truth) cho toàn bộ thông tin liên quan đến thể thao, bao gồm lịch thi đấu, tỷ số trực tiếp, kết quả, thống kê, và thông tin đội/vận động viên. Nó tổng hợp, làm sạch và phân phối dữ liệu cho các module khác, đặc biệt là Betting và Risk Management. 
o	Nguyên tắc thiết kế quan trọng nhất là Hệ thống không cho phép các module như Betting App hay Admin Panel gọi trực tiếp ra API bên ngoài. Thay vào đó, chỉ duy nhất Sports Data Service có trách nhiệm này. 
o	Hoạt động: Sports Data Service hoạt động như một bộ lọc và kho trung chuyển. Nó sẽ chủ động gọi các API bên ngoài theo một lịch trình được tối ưu, sau đó lưu trữ, làm sạch và chuẩn hóa dữ liệu.
o	Lợi ích: Các module khác trong hệ thống khi cần dữ liệu (ví dụ: Betting Service cần danh sách trận đấu) sẽ gọi đến API nội bộ của Sports Data Service. Lệnh gọi nội bộ này là hoàn toàn miễn phí và cực kỳ nhanh chóng. Điều này giúp hệ thống tách biệt hoàn toàn yêu cầu của người dùng khỏi các lệnh gọi API tốn kém ra bên ngoài.
•	Vai trò trong hệ thống:
o	Cung cấp dữ liệu đầu vào cho 
Betting Service để hiển thị các sự kiện và thị trường cá cược cho người dùng.
o	Cung cấp dữ liệu thô và tỷ lệ cược ban đầu cho 
Risk Management Service để làm cơ sở cho các tính toán rủi ro và điều chỉnh tỷ lệ cược.
o	Đảm bảo tính nhất quán và chính xác của dữ liệu trên toàn hệ thống, tránh sai lệch thông tin giữa các thành phần.
•	Các tính năng chi tiết:
o	Thu thập Dữ liệu Đa nguồn (Data Ingestion): Tích hợp với nhiều API của các nhà cung cấp dữ liệu thể thao bên ngoài để đảm bảo tính dự phòng. Nếu một nguồn gặp sự cố, hệ thống có thể tự động chuyển sang nguồn thay thế.
o	Chuẩn hóa và Làm sạch Dữ liệu (Normalization & Cleansing): Dữ liệu từ các nhà cung cấp khác nhau thường có định dạng không đồng nhất (ví dụ: tên đội bóng, tên giải đấu). Service này sẽ chuẩn hóa tất cả dữ liệu về một định dạng chung, đồng thời loại bỏ các thông tin trùng lặp hoặc sai sót.
o	Xác thực và Đối chiếu Chéo (Validation & Reconciliation): Tự động so sánh dữ liệu từ các nguồn khác nhau để xác thực tính chính xác. Ví dụ, nếu một bàn thắng được ghi nhận, hệ thống sẽ kiểm tra xem thông tin này có khớp giữa các nguồn hay không trước khi cập nhật.
o	Cơ chế Xử lý Lỗi và Độ trễ:
	Hàng đợi (Queueing): Các dữ liệu thô từ API sẽ được đưa vào một hàng đợi để xử lý bất đồng bộ, tránh làm nghẽn hệ thống.
	Cảnh báo (Alerting): Thiết lập hệ thống cảnh báo tự động cho đội ngũ kỹ thuật khi một nguồn API ngừng hoạt động, trả về dữ liệu bất thường, hoặc có độ trễ cao.
	Logic Dự phòng (Failover Logic): Nếu dữ liệu chính bị trễ hoặc lỗi, hệ thống có thể tạm thời hiển thị thông tin từ nguồn phụ hoặc tạm ẩn thị trường đó để chờ xác thực, thay vì hiển thị dữ liệu sai. Để tăng cường khả năng phục hồi, các cơ chế sau sẽ được áp dụng:
	Mô hình Ngắt mạch (Circuit Breaker Pattern): Nếu một nguồn API liên tục trả về lỗi hoặc có độ trễ cao, hệ thống sẽ tạm thời "ngắt" kết nối đến nguồn đó trong một khoảng thời gian ngắn để tránh làm ảnh hưởng đến toàn bộ hệ thống, sau đó thử lại.
	Nguồn Dữ liệu Dự phòng (Fallback Data Source): Trong trường hợp nguồn dữ liệu chính bị lỗi, hệ thống sẽ tự động chuyển sang một nguồn dữ liệu phụ đã được xác định trước.
	Cơ chế Ghi đè Thủ công (Manual Override): Trong các trường hợp đặc biệt nghiêm trọng, Admin sẽ có quyền ghi đè hoặc xác nhận kết quả một sự kiện theo cách thủ công thông qua Admin Panel để đảm bảo hoạt động không bị gián đoạn.
o	Cung cấp API Nội bộ (Internal API Serving): Cung cấp các API nội bộ, hiệu suất cao và có cơ chế caching mạnh mẽ để các service khác truy vấn dữ liệu một cách nhanh chóng và hiệu quả.
•	Chiến Lược Tối Ưu Hóa Lượt Gọi và Chi Phí API
Để đảm bảo tính bền vững về mặt tài chính và hiệu suất hoạt động, hệ thống áp dụng một chiến lược đa lớp nhằm tối ưu hóa và giảm thiểu số lượt gọi đến các API bên ngoài vốn rất tốn kém. Chiến lược này đặc biệt quan trọng để tránh việc nhanh chóng chạm giới hạn (rate limiting) và kiểm soát chi phí vận hành.
o	Kiến trúc tập trung (Centralized Control): Nguyên tắc cốt lõi là chỉ duy nhất Module Dữ Liệu Thể Thao (Sports Data Service) được phép giao tiếp với các API bên ngoài. Các module khác như Betting Service hay Risk Management Service tuyệt đối không gọi trực tiếp ra ngoài mà phải thông qua API nội bộ do Sports Data Service cung cấp. Điều này tạo ra một điểm kiểm soát duy nhất, giúp việc tối ưu hóa trở nên khả thi.
o	Cập nhật theo chu kỳ (Scheduled Updates), không theo yêu cầu (On-Demand): Hệ thống không thực hiện một lượt gọi API mỗi khi có người dùng truy cập. Thay vào đó, Sports Data Service sẽ chủ động gọi các API bên ngoài theo một lịch trình định sẵn (ví dụ: mỗi 1-5 phút, tùy thuộc vào tầm quan trọng của dữ liệu và tần suất làm mới của nhà cung cấp). Dù có 1 hay 10,000 người dùng truy cập trong khoảng thời gian đó, hệ thống cũng chỉ thực hiện một vài lượt gọi API theo lịch trình, giúp tiết kiệm chi phí một cách đáng kể.
o	Lớp bộ nhớ đệm (Cache Layer) là tuyến phòng thủ đầu tiên: Tất cả dữ liệu thường xuyên được truy cập như lịch thi đấu của các giải lớn, thông tin các sự kiện sắp diễn ra sẽ được lưu trữ trong một lớp bộ nhớ đệm (Cache Layer) hiệu suất cao. Khi người dùng yêu cầu thông tin này, hệ thống sẽ trả về dữ liệu từ cache ngay lập tức, giảm độ trễ và loại bỏ hoàn toàn nhu cầu gọi lại thêm bất kỳ lệnh gọi API nào ra ngoài cho những yêu cầu trùng lặp. Lệnh gọi API ra bên ngoài chỉ xảy ra khi dữ liệu trong cache hết hạn hoặc khi hệ thống cần cập nhật thông tin mới.
o	Xử lý bất đồng bộ (Asynchronous Processing): Dữ liệu thô từ API sẽ được đưa vào một hàng đợi (Message Queue) để xử lý bất đồng bộ. Điều này giúp quá trình thu thập và làm sạch dữ liệu diễn ra độc lập, không làm nghẽn các tác vụ khác và đảm bảo hệ thống luôn phản hồi nhanh chóng với người dùng, trong khi luồng cập nhật dữ liệu nền vẫn hoạt động hiệu quả.
o	Nhờ các cơ chế này, Sports Data Service hoạt động như một "tấm khiên" thông minh, tạo ra một bộ đệm vững chắc giữa các yêu cầu từ người dùng và các API đắt đỏ bên ngoài, qua đó đảm bảo hệ thống hoạt động hiệu quả, tiết kiệm và có khả năng mở rộng.
•	Lộ trình Xử lý Xung đột Dữ liệu Tự động
Để đảm bảo tốc độ và tính chính xác khi có xung đột dữ liệu từ các API, hệ thống sẽ triển khai lộ trình xử lý 3 giai đoạn:
o	Giai đoạn 1: Tối ưu hóa Quy trình Thủ công (MVP)
	Xây dựng một "Bảng điều khiển Xử lý Xung đột" chuyên dụng. Đội ngũ vận hành sẽ sử dụng một giao diện chuyên biệt để xem dữ liệu từ tất cả các nguồn và đưa ra quyết định xác nhận hoặc hủy bỏ sự kiện theo cách thủ công.
	Khi có xung đột thì tạm ngưng thị trường: Các thị trường cược liên quan sẽ bị tạm khóa để ngăn ngừa rủi ro, giao diện hiển thị rõ ràng thông tin từ các nguồn đang mâu thuẫn, gắn cờ cảnh báo: 
	Một cảnh báo sẽ được gửi đến Bảng điều khiển của đội ngũ vận hành.
	Giao diện phải hiển thị rõ ràng: Thông tin từ các nguồn API đang xung đột (API A: Goal at 20:35:10, API B: No Goal at 20:35:12).
	Các nút hành động dứt khoát: "Xác nhận Bàn thắng", "Hủy Bàn thắng", "Tạm đóng thị trường".
	Xây dựng Quy trình Vận hành Chuẩn (SOP) và Phân cấp Nguồn Tin:
Định nghĩa một hệ thống phân cấp độ tin cậy của nguồn tin (Source Tiering). Ví dụ:
	Tier 1: Trang web chính thức của giải đấu.
	Tier 2: Kênh truyền hình lớn (ESPN, Sky Sports).
	Tier 3: Các API dữ liệu trả phí.
	Admin phải tuân thủ quy trình này để đưa ra quyết định cuối cùng.
	Thiết lập SLA (ví dụ: xử lý trong 60 giây) cho đội ngũ vận hành.
o	Giai đoạn 2: Bán Tự Động Hóa (Hỗ trợ ra quyết định)
	Tự động thu thập bằng chứng: Khi hệ thống phát hiện xung đột, nó không chỉ cảnh báo mà còn tự động truy cập vào các nguồn tin Tier 1, Tier 2 (đã được định nghĩa trong SOP) để lấy thông tin xác thực từ các nguồn tin được định nghĩa là "Nguồn Chân lý" (ví dụ: trang chủ giải đấu).
	Hệ thống sẽ đưa ra một gợi ý quyết định cho Admin (ví dụ: "Gợi ý: Xác nhận Bàn thắng vì đã được xác thực trên PremierLeague.com"). 
	Vai trò của Admin là xác minh và phê duyệt.
o	Giai đoạn 3: Tự Động Hóa Hoàn Toàn (Dựa trên cấp độ tin cậy)
	Hệ thống sẽ được cấu hình với các cấp độ tin cậy (Trust Tiers) cho từng nguồn API.
	Hệ thống sẽ tự động giải quyết xung đột bằng cách ưu tiên tin vào nguồn có cấp độ tin cậy cao hơn. Can thiệp thủ công chỉ cần thiết khi các nguồn có cùng độ tin cậy cao xung đột với nhau.
•	Các Nhà Cung Cấp API Được Lựa Chọn (Giai đoạn MVP)
Để khởi động dự án, giai đoạn MVP sẽ tích hợp với hai nhà cung cấp API, mỗi nhà cung cấp phục vụ một mục đích chuyên biệt và tách bạch:
o	API-Sports.io (Nguồn Dữ Liệu Sự Kiện & Thị Trường): 
	Vai trò: Với mỗi sự kiện thể thao, hệ thống sẽ ưu tiên gọi đến API-Sports để lấy danh sách tất cả các loại hình cược (markets) mà họ hỗ trợ cho sự kiện đó. Đây là nguồn để xác định sự đa dạng các cửa cược có thể hiển thị cho người dùng được sử dụng làm nguồn chính để lấy các dữ liệu nền tảng về thể thao như: lịch thi đấu, thông tin giải đấu, thông tin đội/vận động viên, kết quả trận đấu, và quan trọng nhất là danh sách các loại thị trường cược (markets) có sẵn cho một sự kiện.
	Lý do chọn: Cung cấp độ phủ dữ liệu rộng, giúp hệ thống tự động tạo ra cấu trúc của một trận đấu với các cửa cược cần thiết mà không cần Admin nhập liệu thủ công.
o	The-Odds-API.com (Nguồn Tham Khảo Tỷ Lệ Cược - Chỉ Dành Cho Admin): 
	Vai trò: Đối với 3 loại cược chính và có thanh khoản cao nhất là Moneyline (Thắng-Thua), Spreads (Cược Chấp), và Totals (Tài-Xỉu), hệ thống sẽ tham chiếu chéo hoặc ưu tiên lấy dữ liệu tỷ lệ cược từ The Odds API. Lý do là vì nhà cung cấp này chuyên tổng hợp tỷ lệ từ nhiều nhà cái lớn, cung cấp một cái nhìn thị trường chính xác hơn cho các loại cược cốt lõi này. Đây là nguồn dữ liệu tham khảo nội bộ, bí mật, không bao giờ được hiển thị cho người dùng cuối. Dữ liệu tỷ lệ cược từ API này sẽ được hiển thị chỉ trong Admin Panel để Super Admin và các Admin được chỉ định sử dụng làm cơ sở tham khảo khi thiết lập tỷ lệ cược ban đầu (opening odds) cho các sự kiện trên nền tảng. 
	Lý do chọn: Cung cấp một cái nhìn tổng quan về tỷ lệ của thị trường chung, giúp Admin đưa ra quyết định "mở kèo" ban đầu một cách hợp lý và cạnh tranh.
o	Chiến lược tích hợp và Luồng dữ liệu:
Sports Data Service sẽ hoạt động như một bộ lọc và phân phối thông tin:
	Dữ liệu sự kiện (lịch thi đấu, tên đội, các loại cược khả dụng) từ API-Sports.io sẽ được đẩy đến Betting Service để tạo ra các sự kiện trên giao diện người dùng và đến Risk Management Service để tạo cấu trúc cho việc quản lý.
	Dữ liệu tỷ lệ cược tham khảo từ The-Odds-API.com sẽ được đẩy duy nhất đến Admin Panel.
	Hệ thống sẽ không bao giờ tự động sử dụng tỷ lệ cược từ API cho người dùng. Tỷ lệ cược mà người dùng nhìn thấy là do Risk Management Service của nền tảng toàn quyền quyết định và cung cấp.
o	Quy trình Xử lý Thủ công: Đối với các thị trường cược mà cả hai API đều không cung cấp, chúng sẽ được quản lý thông qua giao diện Admin, nơi các quản trị viên có thể tạo sự kiện và thiết lập tỷ lệ theo cách thủ công.
Module Ví Đa Tiền Tệ và Trao Đổi Hối Đoái (Multi-Currency Wallet & Exchange)
•	Chức năng chính: Cung cấp một hệ thống ví điện tử an toàn và linh hoạt, cho phép người dùng quản lý tài sản bằng nhiều loại tiền tệ khác nhau và thực hiện các giao dịch tài chính trong hệ thống.
•	Vai trò trong hệ thống: Module này là trung tâm quản lý dòng tiền của người dùng, tương tác chặt chẽ với Module Betting để trừ tiền khi đặt cược và cộng tiền khi thắng cược, đồng thời tích hợp với các cổng thanh toán để xử lý nạp/rút.
•	Các tính năng chi tiết: 
o	Quản lý cơ bản: Cho phép người dùng thực hiện các tính năng nạp, rút, gửi tiền và kiểm tra số dư cho từng loại tiền tệ.
o	Quy trình rút tiền linh hoạt:
	Rút tiền miễn phí có điều kiện: Người dùng có thể đặt lệnh rút tiền miễn phí nếu đạt mức tối thiểu. Luồng hoạt động như sau: 
	Ngay khi đặt lệnh, người dùng nhận được một thông báo tức thì xác nhận đã lên lịch rút tiền sau 45 ngày.
	Trong suốt 44 ngày chờ, người dùng vẫn có toàn quyền sử dụng số tiền trong ví để tham gia các hoạt động khác.
	Vào ngày thứ 42, hệ thống sẽ kiểm tra số dư. Nếu số dư không đủ để thực hiện lệnh rút, hệ thống sẽ không gửi email và lệnh rút có thể bị hủy.
	Nếu số dư đủ, hệ thống sẽ gửi một email xác nhận đến người dùng. Email này chứa một đường link hoặc nút nhấn có hiệu lực trong 48 giờ.
	Nếu người dùng không xác nhận trong 48 giờ, lệnh rút sẽ tự động bị hủy bỏ.
	Trong thời gian chờ đợi thì người dùng vẫn có quyền sử dụng lượng tiền có ý định rút cho các hoạt động trong nền tảng nhé chứ không phải bị khóa cứng lại gây khó chịu cho người dùng
	Rút tiền tức thời: Cung cấp tùy chọn rút tiền ngay lập tức nhưng người dùng sẽ phải chịu một mức phí do hệ thống quy định.
	Giao dịch nội bộ: Hỗ trợ người dùng cá nhân gửi tiền cho các tài khoản cá nhân khác trong hệ thống.
	Trao đổi hối đoái: Cho phép người dùng trao đổi tiền tệ với hệ thống theo tỷ giá được quản lý bởi Super Admin và Admin.
o	Chiến lược Vận hành và Xây dựng Lòng tin cho Quy trình Rút tiền 45 ngày
Quy trình rút tiền miễn phí có điều kiện trong 45 ngày là một chiến lược kinh doanh cốt lõi nhằm tạo ra nguồn vốn lưu động (float) để trang trải chi phí vận hành, qua đó duy trì một nền tảng miễn phí cho người dùng. Để chiến lược này thành công và bền vững, các yếu tố sau phải được triển khai một cách nghiêm ngặt:
	1. Minh Bạch Tuyệt Đối và Truyền Thông Chủ Động:
	Truyền thông ngay từ đầu: Quy trình 45 ngày phải được nêu bật và giải thích một cách rõ ràng, đơn giản ngay trên trang đăng ký, trang nạp tiền và trang hướng dẫn.
	Ngôn ngữ trung thực: Thay vì chỉ nói "rút tiền miễn phí", cần sử dụng ngôn ngữ rõ ràng như: "Chúng tôi cung cấp hai lựa chọn: Rút tiền Miễn phí với lịch trình 45 ngày, hoặc Rút tiền Tức thời với một khoản phí nhỏ. Lựa chọn này giúp chúng tôi duy trì nền tảng hoàn toàn miễn phí cho bạn."
	Xây dựng trang FAQ chi tiết: Cần có một trang riêng giải thích cặn kẽ TẠI SAO lại có chính sách này, lợi ích cho người dùng (duy trì nền tảng miễn phí), và cam kết của nền tảng về việc thanh toán đúng hạn.
	2. Xây Dựng Lòng Tin Bằng Sự Hoàn Hảo ở Mọi Điểm Chạm Khác:
	Thực thi thanh toán không sai sót: Các khoản rút tiền vào đúng ngày thứ 45 phải được thực hiện chính xác tuyệt đối, không được có bất kỳ sự chậm trễ hay sai sót nào.
	Dịch vụ Hỗ trợ Khách hàng (CS) xuất sắc: Đội ngũ CS phải được đào tạo để trở thành những người trấn an chuyên nghiệp, am hiểu chính sách, trả lời nhanh chóng và đồng cảm với sự lo lắng của người dùng về tiền bạc.
	Tận dụng "Bằng chứng Xã hội" (Social Proof): Tận dụng tối đa Module Lập nhóm & Cộng đồng để khuyến khích các nhóm và người dùng uy tín chia sẻ trải nghiệm rút tiền thành công, đúng hạn.
o	Chiến lược Vận hành và Xây dựng cho Rút tiền tức thời (Mô hình Phí Linh hoạt "Giá Tốt Hơn")
Để cung cấp một lựa chọn công bằng và tạo ra trải nghiệm tích cực cho người dùng, hệ thống sẽ áp dụng một mô hình tính phí rút tiền tức thời linh hoạt, dựa trên nguyên tắc luôn mang lại mức giá tốt hơn cho người dùng.
	Luồng Hoạt Động Chi Tiết:
	Bước 1: Thiết lập và Công bố "Phí Trần" (The Surface Fee)
Nền tảng sẽ nghiên cứu và đưa ra một biểu phí tiêu chuẩn (ví dụ: 20.000 VNĐ + 5%). Biểu phí này được công bố rộng rãi, minh bạch và đóng vai trò là mức phí tối đa mà một người dùng có thể phải trả.
	Bước 2: Tính toán "Phí Cá nhân" Âm thầm (The Silent Personalized Fee Calculation)
Khi người dùng yêu cầu rút tiền tức thời, hệ thống sẽ tính toán "Phí Cá nhân" của người dùng đó dựa trên thuật toán bình quân gia quyền về chi phí nạp tiền trong lịch sử của họ.
	Bước 3: Áp dụng Quy tắc "Luôn có lợi cho Người dùng"
Hệ thống sẽ so sánh "Phí Cá nhân" và "Phí Trần".
	NẾU (Phí Cá nhân) < (Phí Trần) thì hệ thống sẽ tự động áp dụng Phí Cá nhân thấp hơn cho giao dịch đó.
	NGƯỢC LẠI NẾU (Phí Cá nhân) > (Phí Trần) thì, hệ thống sẽ áp dụng Phí Trần cho giao dịch đó.
	Bước 4: Ghi nhận "Chiết khấu" và Truyền thông Tới Người dùng
Ghi nhận nội bộ: Khoản chênh lệch khi áp dụng mức phí thấp hơn sẽ được ghi nhận lại để phục vụ việc phân tích và điều chỉnh "Phí Trần" trong tương lai.
Hiển thị cho người dùng: Giao diện sẽ hiển thị rõ ràng sự ưu đãi này. Ví dụ: "Phí rút tiền tiêu chuẩn: 95.000 VNĐ. Phí ưu đãi dành riêng cho bạn hôm nay: 57.500 VNĐ! Do bạn thường sử dụng các phương thức nạp tiền hiệu quả, chúng tôi đã giảm phí cho bạn."
Module Lập Nhóm và Tương Tác Cộng Đồng (Grouping & Community Interaction)
•	Chức năng chính: Xây dựng một không gian tương tác xã hội, cho phép người dùng thành lập các nhóm (syndicate) để cùng nhau góp vốn, chia sẻ lợi nhuận, rủi ro và kinh nghiệm cá cược.
•	Vai trò trong hệ thống: Module này thúc đẩy sự tương tác và gắn kết của người dùng, biến nền tảng từ một nơi cá cược đơn thuần thành một cộng đồng. Nó quản lý các quỹ chung, phân quyền và các hoạt động tập thể.
•	Vai Trò Nhà Cái: Cá Nhân, Nhóm và Admin
o	Một trong những tính năng cốt lõi của hệ thống là cho phép nhiều đối tượng khác nhau hoạt động với tư cách là một nhà cái. Hệ thống mặc định cho phép bên phát hành phiếu cược có thể là:
	Người dùng cá nhân: Sử dụng tài chính cá nhân.
	Nhóm người dùng: Sử dụng tài chính chung của nhóm do các thành viên đóng góp.
	Admin hệ thống: Do Super Admin chỉ định và cấp vốn từ hệ thống.
o	Các nhà cái này có quyền tạo, mua, bán các phiếu cá cược thể thao và quản lý trận đấu với các đặc điểm sau:
	Quyền quản lý trận đấu:
	Điều chỉnh tỷ lệ cược: Có quyền điều chỉnh tỷ lệ của các phiếu cược còn lại, chưa có người sở hữu, trong suốt thời gian phát hành.
	Hủy bỏ phát hành: Có quyền hủy sự kiện trước thời điểm trận đấu bắt đầu.
	Tạm ngưng phát hành: Có quyền tạm dừng việc bán phiếu cược trong thời gian phát hành nhưng không được vô hiệu hóa các phiếu đã có người sở hữu.
	Đặt ngưỡng rủi ro: Có quyền tự đặt ngưỡng rủi ro cho sự kiện. Nếu nhà cái cá nhân/nhóm không đặt, hệ thống sẽ mặc định ngưỡng rủi ro bằng với số vốn bỏ ra để tạo sự kiện đó. Đối với admin hệ thống, việc đặt ngưỡng rủi ro là bắt buộc theo yêu cầu của Super Admin.
	Đặt tỷ lệ cash-out: Có quyền thiết lập Cash-out cho sự kiện mong muốn.
•	Giải pháp đảm bảo an toàn và minh bạch cho vai trò nhà cái cá nhân và nhóm
Để triển khai tính năng phức tạp này một cách có trách nhiệm, hệ thống sẽ áp dụng một giải pháp 3 lớp nhằm bảo vệ cả người dùng và nền tảng:
o	Lớp 1: Khung Pháp lý & Điều khoản Ràng buộc
	Điều khoản Dịch vụ riêng biệt: Người dùng phải đồng ý với một bộ "Điều Khoản Dịch Vụ dành cho Nhà Cái Cá Nhân và nhóm" trước khi kích hoạt tính năng. Điều khoản này sẽ nhấn mạnh Tuyên bố Miễn trừ Trách nhiệm Rõ ràng: Nền tảng chỉ cung cấp công cụ, không phải là nhà tư vấn tài chính. Mọi quyết định về tỷ lệ cược, quản lý vốn và rủi ro đều là trách nhiệm duy nhất của người dùng. Nên người dùng cần hiểu rõ các khái niệm cốt lõi như "Trách nhiệm chi trả (Liability)", "Ngưỡng Rủi Ro" và việc quản lý rủi ro trước khi được cấp quyền.
o	Lớp 2: Hỗ trợ & Giáo dục Người dùng * 
	Cổng thông tin Giáo dục: Xây dựng khu vực FAQ và video hướng dẫn chi tiết cách hoạt động của các công cụ quản lý rủi ro, đặc biệt là công cụ mô phỏng.
	Đội ngũ Hỗ trợ Chuyên biệt: Đào tạo đội ngũ hỗ trợ để giải đáp thắc mắc về tính năng, nhưng không đưa ra lời khuyên tài chính.
o	Lớp 3: Ràng buộc Kỹ thuật
	Ghi nhận Lựa chọn Không thể thay đổi: Lựa chọn của người dùng (quản lý thủ công hoặc tự động) sẽ được ghi lại vĩnh viễn cho mỗi sự kiện họ tạo ra. `Risk Management Service` sẽ dựa vào lựa chọn này để áp dụng hoặc bỏ qua các cơ chế bảo vệ, đảm bảo tính minh bạch khi có tranh chấp.
•	 Các tính năng chi tiết: 
o	Tạo và tham gia nhóm: Người dùng có thể lập nhiều nhóm (có hoặc không có mật khẩu) và tham gia nhiều nhóm khác nhau. Mỗi nhóm sẽ hoạt động với một loại tiền tệ duy nhất do trưởng nhóm chỉ định ban đầu.
o	Quản lý vốn nhóm: 
	Các thành viên có thể đóng góp vốn để chia sẻ lợi nhuận và rủi ro. Để đảm bảo khả năng thanh toán cho các sự kiện do nhóm tổ chức, vốn của mỗi thành viên trong quỹ nhóm sẽ được chia thành hai loại rõ ràng:
	Vốn Khả dụng (Available Capital): Là phần vốn không bị ràng buộc bởi bất kỳ trách nhiệm chi trả nào từ các sự kiện đang hoạt động. Thành viên có toàn quyền rút phần vốn này bất kỳ lúc nào.
	Vốn Rủi ro (At-Risk Capital): Là phần vốn đã được hệ thống "tạm khóa" để đảm bảo cho các Trách nhiệm Chi trả (Liability) tiềm năng của các sự kiện mà nhóm đang tổ chức. Phần vốn này sẽ không thể rút cho đến khi các sự kiện đó kết thúc và được thanh toán.
	Luồng hoạt động: Khi một nhóm tạo sự kiện, Risk Management Service sẽ tính toán Liability tối đa và tạm khóa một lượng vốn tương ứng từ quỹ nhóm. Số vốn này sẽ được giải phóng (và cộng/trừ lãi/lỗ) ngay khi sự kiện kết-thúc.
	Nhóm sẽ tự động giải tán sau 30 ngày không có hoạt động, và vốn sẽ được trả về ví các thành viên.
o	Phân quyền trong nhóm: 
	Quyền của Trưởng nhóm: 
	Phân chia nhiệm vụ cụ thể cho thành viên (tạo phiếu cược, mua/bán phiếu, điều chỉnh tỷ lệ cược, đặt ngưỡng rủi ro, thiết lập cash-out) với ngân sách được trích từ quỹ nhóm.
	Trao lại chức vị trưởng nhóm cho người dùng khác (không nhất thiết phải là thành viên trong nhóm).
	Đóng hoặc mở cửa để nhận thêm thành viên và vốn góp.
	Chặn chat của các thành viên gây rối trong kênh chat chung.
	Giới hạn của Trưởng nhóm và các thành viên: 
	Trưởng nhóm không có quyền loại bỏ bất kỳ thành viên nào đang có đóng góp vốn vào nhóm.
	Không ai trong nhóm, kể cả trưởng nhóm, có quyền rút vốn của thành viên khác về ví riêng của mình.
	Quyền của mọi thành viên: 
	Kiểm tra số dư và lịch sử hoạt động của nhóm.
	Chủ động chặn tin nhắn từ thành viên xác định mà họ không muốn nhận.
	Tự thiết lập bộ lọc để ẩn các từ ngữ mà cá nhân họ cho là không phù hợp.
	Mọi thành viên có quyền kiểm tra số dư và lịch sử hoạt động chi tiết của nhóm.
	Quy trình Xử lý Tự động khi Trưởng nhóm Không hoạt động
Để đảm bảo một nhóm có thể tiếp tục hoạt động bền vững ngay cả khi người lãnh đạo không còn hoạt động, hệ thống sẽ áp dụng một cơ chế chuyển giao quyền lực tự động.
	Định nghĩa "Không hoạt động": Một trưởng nhóm được coi là không hoạt động nếu họ không đăng nhập vào hệ thống trong một khoảng thời gian quy định (ví dụ: 30 ngày), trong khi nhóm vẫn có các hoạt động khác từ thành viên.
Khi phát hiện một trưởng nhóm không hoạt động, hệ thống sẽ tự động tìm người kế nhiệm và thăng cấp cho họ theo các quy tắc ưu tiên sau:
1. Trường hợp trong nhóm CÓ người được phân quyền "Tạo Sự Kiện": Hệ thống sẽ chọn người kế nhiệm trong số những thành viên này dựa trên hệ thống ưu tiên 3 cấp:
	Ưu tiên 1: Thành viên có vốn góp cao nhất.
	Ưu tiên 2 (Nếu vốn góp bằng nhau): Thành viên đã tạo ra nhiều sự kiện nhất cho nhóm.
	Ưu tiên 3 (Nếu các tiêu chí trên vẫn bằng nhau): Thành viên có tỷ suất lợi nhuận bình quân cao nhất.
2. Trường hợp trong nhóm KHÔNG có ai được phân quyền "Tạo Sự Kiện" (Cơ chế dự phòng): Hệ thống sẽ chọn người kế nhiệm trong số tất cả các thành viên còn lại dựa trên hệ thống ưu tiên 2 cấp:
	Ưu tiên 1: Thành viên có vốn góp cao nhất.
	Ưu tiên 2 (Nếu vốn góp bằng nhau): Thành viên tham gia nhóm sớm nhất và vẫn đang hoạt động.
Sau khi người kế nhiệm được xác định, hệ thống sẽ tự động thăng cấp cho họ thành Trưởng nhóm mới và giáng cấp trưởng nhóm cũ xuống làm thành viên thường không có quyền điều hành.
	Quy trình Xử lý khi Trưởng nhóm Chủ động Trao quyền
Trưởng nhóm hiện tại có toàn quyền chủ động chỉ định một người dùng khác làm người kế nhiệm. Đây là một hành động tự nguyện và độc lập với quy tắc xử lý khi không hoạt động.
	Trường hợp chỉ định thành viên trong nhóm: Việc chuyển giao được thực hiện ngay lập tức.
	Trường hợp đặc biệt: Chỉ định "Người Ngoài Nhóm": Để bảo vệ quyền lợi của các thành viên hiện tại, khi trưởng nhóm chỉ định một người chưa phải là thành viên trong nhóm, hệ thống sẽ kích hoạt một quy trình bỏ phiếu tín nhiệm 2 vòng:
	Vòng 1: Bỏ Phiếu Tín Nhiệm của "Ban Điều Hành"
	Một yêu cầu bỏ phiếu sẽ được gửi đến tất cả các thành viên đang có quyền điều hành trong nhóm.
	Việc chuyển giao được thông qua nếu trên 50% số thành viên này đồng ý. Nếu thành công, quy trình kết thúc. Nếu thất bại, quy trình chuyển sang Vòng 2.
	Vòng 2: Bỏ Phiếu Tín Nhiệm của "Toàn Thể Cổ Đông" (Fallback)
	Vòng này chỉ diễn ra khi Vòng 1 thất bại. Một yêu cầu bỏ phiếu sẽ được gửi đến tất cả các thành viên trong nhóm.
	Quyền biểu quyết của mỗi thành viên sẽ được tính theo tỷ lệ vốn góp của họ trong nhóm.
	Việc chuyển giao được thông qua nếu tổng số vốn của các thành viên đồng ý chiếm trên 50% tổng số vốn của toàn bộ nhóm.
	Nếu Vòng 2 cũng thất bại, yêu cầu chuyển giao quyền lực sẽ bị hủy bỏ.
o	Sáp nhập nhóm: Hỗ trợ sáp nhập các nhóm sử dụng cùng một loại tiền tệ với nhau.
o	Live Chat: Tích hợp kênh chat riêng cho các cá nhân và trong mỗi nhóm, giúp các thành viên trao đổi thông tin. Người dùng có quyền thiết lập để ẩn các từ ngữ hoặc ẩn các tin nhắn từ những đối tượng cụ thể mà họ cho là không phù hợp. Việc ẩn này chỉ áp dụng cho cá nhân họ, những người khác trong kênh chat vẫn sẽ thấy nội dung đó nếu họ không tự chặn.
o	Tương tác liên nhóm
	Đóng góp vốn chéo nhóm: Cho phép một nhóm người dùng này có thể đóng góp vốn vào một nhóm người dùng khác để cùng chia sẻ lợi nhuận và rủi ro, nhưng không có khả năng nắm giữ bất kỳ quyền điều hành nào trong nhóm nhận vốn góp.
	Sáp nhập nhóm: Hỗ trợ sáp nhập các nhóm sử dụng cùng một loại tiền tệ với nhau.
•	Hệ thống Đánh giá và Uy tín trên Sàn P2P:
o	Rating và Review: Sau mỗi giao dịch thành công trên sàn P2P, người mua và người bán có thể để lại đánh giá và nhận xét cho nhau.
o	Huy hiệu Uy tín (Badges): Hệ thống sẽ tự động trao các huy hiệu cho người dùng có lịch sử giao dịch tốt, đánh giá cao, và hoạt động tích cực để những người dùng khác có thể nhận diện.
o	Danh sách Đen (Blacklist): Những người dùng vi phạm quy tắc của sàn giao dịch, có hành vi lừa đảo hoặc nhận nhiều đánh giá tiêu cực sẽ bị đưa vào danh sách đen và hạn chế hoặc cấm giao dịch.
Module Khuyến Mãi (Promotions Module)
•	Chức năng chính: Cung cấp một nền tảng linh hoạt cho phép không chỉ admin hệ thống mà cả người dùng cá nhân và các nhóm có thể tự tạo ra các chương trình khuyến mãi để thu hút người chơi khác. 
•	Vai trò trong hệ thống: Tương tác chặt chẽ với Module Quản Lý Rủi Ro để đảm bảo mọi chương trình khuyến mãi, dù do hệ thống hay người dùng tạo ra, đều được kiểm soát trong một ngưỡng rủi ro phụ an toàn.
•	Các tính năng chi tiết: 
o	Người dùng tự tạo khuyến mãi: Cho phép cá nhân hoặc nhóm tạo và chia sẻ các mã khuyến mãi (tặng tiền, hoàn tiền, ...) để thu hút người khác đặt cược vào các sự kiện do họ phát hành.
o	Các loại hình khuyến mãi được hỗ trợ:
	Gift Money (Tặng tiền): Tặng một khoản tiền thưởng (ví dụ: "nhập code 'ABC123' để nhận 50.000 VNĐ") chỉ được dùng cho một sự kiện của bên phát hành. 
	Cơ chế khóa tiền của bên phát hành: Khi một người dùng sử dụng tiền tặng này, một lượng tiền tương đương với (phần lợi nhuận thắng cược + phần tiền tặng) sẽ tính vào trong Trần Cố Định Phụ của 1 sự kiện của bên phát hành khuyến mãi.
	Nếu người dùng sử dụng tiền tặng bị thua, khoản tiền tạm khóa trong Trần Cố Định Phụ của 1 sự kiện sẽ được mở lại cho bên phát hành.
	Nếu người dùng sử dụng tiền tặng thắng cược, bên phát hành sẽ mất khoản tiền tạm khóa này, và nó sẽ được chuyển vào ví của người thắng cược.
	Cashback (Hoàn tiền): Hoàn lại một phần trăm số tiền đã thua hoặc tổng tiền đã cược cho người chơi ngay sau sự kiện. Ví dụ: "Hoàn trả 0.5% tổng tiền cược hàng ngày, không giới hạn!" hoặc "Hoàn trả 10% tiền thua sau mỗi sự kiện!"
	Bonus Odds (Tăng tỷ lệ): Cung cấp tỷ lệ cược cao hơn bình thường cho một kết quả cụ thể.
	Free Bet (Cược miễn phí): Cung cấp một phiếu cược miễn phí. Tùy vào thiết lập, người thắng cược nhận tiền lãi của phiếu cược. Ví dụ: "Đặt 500.000 VNĐ để nhận 100.000 VNĐ cược miễn phí" hoặc một kịch bản phức tạp hơn như: "Phải đặt tối thiểu cứ mỗi 5 trận trong khoảng thời gian nhất định để nhận ngay cược miễn phí tương đương 20% tổng số chi tiêu trước đó cho trận đấu tiếp theo!"
	Tất cả Khuyến mãi chỉ thật sự kích hoạt khi Trần Cố Định Phụ của 1 sự kiện của bên phát hành có đủ số dư cho KHOẢN TIỀN THƯỞNG TIỀM NĂNG CỦA PROMOTION ĐƯỢC SỬ DỤNG.
•	Quy tắc sử dụng: Hệ thống phải có thông báo rõ ràng cho người dùng về việc khuyến mãi sẽ được ưu tiêns sử dụng khuyến mãi trước khi trừ vào số dư trong ví của người dùng. Người dùng chỉ được phép sử dụng một khuyến mãi cho một sự kiện.
•	Cơ chế Quản lý Rủi ro Chi tiết cho Khuyến mãi do Cộng đồng tạo
Để đảm bảo tính an toàn và khả thi về mặt tài chính cho các chương trình khuyến mãi do người dùng hoặc nhóm tạo ra, hệ thống sẽ áp dụng một bộ quy tắc quản lý ngân sách và xử lý giao dịch chặt chẽ.
o	A. Phân bổ Ngân sách Khuyến mãi (Mô hình Trần Cố Định Chính/Phụ)
	Khi một nhà cái cộng đồng tạo một sự kiện, họ phải xác định Trần Cố Định Tổng (tổng vốn rủi ro).
	Hệ thống sẽ yêu cầu nhà cái lựa chọn một tỷ lệ (ví dụ: 7:3, 8:2, 9:1) để phân chia Trần Cố Định Tổng thành hai phần riêng biệt:
•	Trần Cố Định Chính: Ngân sách dùng để chi trả cho các cược thông thường (không có khuyến mãi).
•	Trần Cố Định Phụ: Ngân sách dành riêng để chi trả cho tất cả các trách nhiệm phát sinh từ các chương trình khuyến mãi (Gift Money, Bonus Odds, Cashback, ...).
	Mọi trách nhiệm chi trả tiềm năng từ một cược có áp dụng khuyến mãi sẽ được tính toán và kiểm tra với số dư còn lại của Trần Cố Định Phụ.
o	B. Quy tắc Xử lý Giao dịch Khuyến mãi
Để giải quyết các mâu thuẫn giữa giá trị khuyến mãi và quy tắc của sự kiện, hệ thống áp dụng các cơ chế sau:
	Cơ chế "Gộp Quỹ" cho Sự kiện Cược Cố Định (Fixed Stake):
•	Tình huống: Một sự kiện yêu cầu mức cược cố định là 20.000 VNĐ, nhưng người chơi có mã "Gift Money" 10.000 VNĐ.
•	Giải pháp: Hệ thống sẽ cho phép người chơi sử dụng 10.000 VNĐ từ khuyến mãi và gộp thêm 10.000 VNĐ từ ví thật của họ để đạt đủ mức cược yêu cầu.
•	Xử lý ngầm: Trách nhiệm chi trả của phiếu cược này sẽ được phân tách và kiểm tra đồng thời với cả hai ngân sách: phần trách nhiệm từ tiền khuyến mãi sẽ tính vào `Trần Cố Định Phụ`, phần trách nhiệm từ tiền thật sẽ tính vào `Trần Cố Định Chính`.
	Quy tắc "Miễn trừ Cược Tối Thiểu" cho Sự kiện Cược Tự Do (Variable Stake):
•	Tình huống: Một sự kiện có mức cược tối thiểu là 20.000 VNĐ, và người chơi có mã "Gift Money" 10.000 VNĐ.
•	Giải pháp: Hệ thống cho phép người chơi đặt cược chỉ với 10.000 VNĐ từ khuyến mãi đó. Quy tắc về mức cược tối thiểu của sự kiện sẽ được miễn trừ cho các giao dịch được tài trợ 100% bằng khuyến mãi. Trách nhiệm chi trả sẽ được kiểm tra với `Trần Cố Định Phụ` như bình thường.

Các Luồng Hoạt Động Chính
Để hiểu rõ cách các module tương tác với nhau, chúng ta sẽ xem xét ba luồng hoạt động chính trong hệ thống:
Luồng Đăng Ký/Đăng Nhập
Luồng này mô tả quá trình người dùng truy cập và xác thực vào hệ thống:
1.	Người dùng truy cập ứng dụng Betting: Người dùng mở ứng dụng Betting (web hoặc mobile) để bắt đầu tương tác với nền tảng cá cược.
2.	Betting gửi yêu cầu xác thực đến Auth: Khi người dùng chọn đăng ký hoặc đăng nhập, Betting sẽ thu thập thông tin cần thiết (tên người dùng, mật khẩu, email, v.v.) và gửi yêu cầu này đến Auth Service.
3.	Auth xử lý đăng ký/đăng nhập: Auth Service sẽ xác minh thông tin đăng nhập (đối với người dùng hiện có) hoặc tạo tài khoản mới và lưu trữ thông tin người dùng (đối với đăng ký mới). Auth cũng sẽ kiểm tra vai trò và quyền hạn của người dùng.
4.	Auth phản hồi kết quả xác thực: Sau khi xử lý, Auth gửi lại kết quả xác thực (thành công/thất bại) và thông tin phiên (ví dụ: token JWT) cho Betting.
5.	Betting hiển thị giao diện phù hợp: Nếu xác thực thành công, Betting sẽ sử dụng thông tin phiên để hiển thị giao diện người dùng phù hợp với vai trò và quyền hạn của người dùng (ví dụ: giao diện người chơi thông thường, hoặc bảng điều khiển admin nếu là quản trị viên). Người dùng có thể bắt đầu khám phá các tính năng cá cược.
Luồng Đặt Cược
Luồng này mô tả quá trình người dùng thực hiện một giao dịch đặt cược:
1.	Người dùng chọn môn thể thao và sự kiện: Từ giao diện Betting, người dùng duyệt qua danh sách các môn thể thao và sự kiện có sẵn (dữ liệu được cung cấp bởi Sports Data Service).
2.	Betting hiển thị tỷ lệ cược: Betting gửi yêu cầu đến Risk Management Service để lấy tỷ lệ cược hiện tại cho sự kiện và các loại cược mà người dùng quan tâm. Risk Management Service sẽ cung cấp tỷ lệ cược hiện tại cho giao diện Betting đã được điều chỉnh động. Quan trọng: Tỷ lệ cược này là tỷ lệ cược độc quyền của hệ thống, được khởi tạo ban đầu bởi Admin và sau đó được Risk Management Service tự động điều chỉnh liên tục dựa trên dòng tiền đặt cược của người dùng trên chính nền tảng, không phụ thuộc vào sự biến động của các nhà cái bên ngoài.
3.	Người dùng chọn loại cược và nhập số tiền: Người dùng chọn một hoặc nhiều loại cược và nhập số tiền muốn đặt cược vào Betting.
4.	Betting gửi yêu cầu đặt cược đến Betting Service: Betting tổng hợp thông tin cược (ID người dùng, sự kiện, loại cược, số tiền, tỷ lệ cược tại thời điểm đặt) và gửi yêu cầu này đến Betting Service.
5.	Betting Service chuyển tiếp yêu cầu đến Risk Management Service: Betting Service không tự mình quyết định chấp nhận cược. Thay vào đó, nó chuyển tiếp yêu cầu đặt cược đến Risk Management Service để kiểm tra rủi ro.
6.	Risk Management Service kiểm tra và tính toán rủi ro: Risk Management Service nhận yêu cầu, tính toán trách nhiệm chi trả tiềm năng mới nếu cược này được chấp nhận. Nó so sánh trách nhiệm này với ngưỡng rủi ro tối đa đã thiết lập. Nếu trách nhiệm vượt ngưỡng, giao dịch sẽ bị từ chối.
7.	Risk Management Service phản hồi kết quả: Risk Management Service gửi lại kết quả (chấp nhận/từ chối) cho Betting Service. Nếu chấp nhận, nó cũng có thể cập nhật tỷ lệ cược cho các cửa liên quan để cân bằng lại rủi ro.
8.	Betting Service xử lý kết quả và cập nhật trạng thái: Betting Service nhận kết quả từ Risk Management Service. Nếu cược được chấp nhận, nó ghi nhận giao dịch vào Transaction Database và cập nhật số dư tài khoản người dùng. Nếu bị từ chối, nó thông báo lý do cho Betting.
9.	Betting thông báo kết quả cho người dùng: Betting hiển thị thông báo cho người dùng về việc đặt cược thành công hay thất bại, và cập nhật thông tin tài khoản nếu cần.
Luồng Quản Lý Rủi Ro (Liên tục)
Luồng này mô tả hoạt động liên tục của Risk Management Service để duy trì sự ổn định tài chính của nhà cái:
1.	Risk Management Service liên tục theo dõi trách nhiệm chi trả: Module này liên tục nhận dữ liệu về các giao dịch đặt cược mới từ Betting Service (thông qua Message Queue hoặc các cơ chế khác). Với mỗi giao dịch, nó tính toán lại tổng trách nhiệm chi trả ròng cho từng kết quả có thể xảy ra của một sự kiện.
2.	Điều chỉnh tỷ lệ cược động dựa trên dòng tiền: Dựa trên sự thay đổi của trách nhiệm chi trả và dòng tiền đổ vào các cửa, Risk Management Service sử dụng thuật toán Dynamic Odds để tự động điều chỉnh tỷ lệ cược. Mục tiêu là khuyến khích người chơi đặt cược vào các cửa có rủi ro thấp hơn để cân bằng lại sổ cược.
3.	Cập nhật tỷ lệ mới cho Betting: Các tỷ lệ cược mới được cập nhật liên tục và cung cấp cho Betting để hiển thị cho người dùng theo thời gian thực.
4.	Kích hoạt phanh khẩn cấp khi cần thiết: Nếu dòng tiền đổ vào một cửa quá lớn và bất thường, khiến trách nhiệm chi trả tiến sát hoặc vượt quá ngưỡng rủi ro tối đa đã thiết lập, Risk Management Service sẽ kích hoạt cơ chế phanh khẩn cấp. Cơ chế này sẽ tự động từ chối các giao dịch mới cho cửa đó và tạm thời khóa việc nhận cược, ngăn chặn nhà cái phải đối mặt với khoản lỗ vượt quá khả năng chi trả.
5.	Ghi nhận và báo cáo: Mọi thay đổi về tỷ lệ cược, các giao dịch bị từ chối, và các sự kiện rủi ro đều được ghi nhận để phục vụ cho việc phân tích và báo cáo sau này, giúp nhà cái đưa ra các quyết định chiến lược và điều chỉnh chính sách rủi ro.

Phân Tích Chuyên Sâu Module Quản Lý Rủi Ro
Module Quản Lý Rủi Ro là trái tim của hệ thống, nơi các nguyên tắc tài chính và thuật toán phức tạp được áp dụng để đảm bảo sự bền vững và lợi nhuận cho nhà cái. Để hiểu rõ hơn về tầm quan trọng và cách thức hoạt động của module này, chúng ta sẽ đi sâu vào bài toán gốc, các nguyên tắc nền tảng và các giải pháp toàn diện được triển khai.
Bài toán gốc và lỗ hổng cốt lõi
Bài toán gốc mà module Quản Lý Rủi Ro giải quyết xuất phát từ một lỗ hổng cơ bản trong mô hình kinh doanh cá cược truyền thống, nơi hoạt động cá cược được coi như việc bán một lô sản phẩm có số lượng giới hạn. Điều này dẫn đến nguy cơ thua lỗ thảm họa nếu không có cơ chế kiểm soát chặt chẽ.
Tình huống minh họa: Giả sử một nhà cái (ABC) phát hành 1.000 phiếu cược với giá $20/phiếu cho một sự kiện thể thao. Tổng doanh thu tối đa có thể đạt được là $20,000. Tỷ lệ cược cố định được đưa ra là: Cửa A (1.85) và Cửa B (2.40).
Kịch bản Thảm họa (Catastrophic Risk): Nếu toàn bộ 1.000 phiếu cược (tương đương $20,000) được mua cho Cửa B, và Cửa B thắng, nhà cái sẽ phải chi trả một khoản tiền thưởng khổng lồ:
•	Tổng Tiền Thưởng Phải Trả = $20,000 x 2.40 = $48,000
•	Khoản Lỗ Ròng = $48,000 (chi) − $20,000 (thu) = $28,000
Lỗ Hổng Cốt Lõi: Lỗ hổng nằm ở việc coi kinh doanh cá cược như bán sản phẩm, trong khi thực tế đây là một hoạt động quản trị rủi ro tài chính. Mô hình ban đầu không có cơ chế nào để kiểm soát Trách Nhiệm Chi Trả (Liability) ‒ tức là tổng nghĩa vụ tài chính mà nhà cái phải thực hiện, bao gồm TỔNG CỦA TẤT CẢ CÁC KHOẢN TIỀN THƯỞNG TIỀM NĂNG của từng phiếu cược đã bán cho một cửa cụ thể cộng với TỔNG CỦA TẤT CẢ CÁC KHOẢN TIỀN THƯỞNG TIỀM NĂNG CỦA PROMOTION. Khi không kiểm soát được Liability, nhà cái có thể đối mặt với những khoản lỗ vượt quá khả năng chi trả, dẫn đến phá sản.
Nguyên tắc nền tảng
Để giải quyết triệt để bài toán gốc, module Quản Lý Rủi Ro được xây dựng dựa trên ba nguyên tắc bất biến, chuyển đổi tư duy từ "bán phiếu" sang "quản lý rủi ro":
1.	Trách Nhiệm Là Nợ Phải Trả (Liability is a Debt): Mọi trách nhiệm chi trả tiềm tàng được xem như một khoản nợ. Khoản nợ này được cộng dồn chứ không phải trừ lùi từ một ngân sách cố định. Điều này nhấn mạnh rằng mỗi phiếu cược được chấp nhận sẽ làm tăng nghĩa vụ tài chính tiềm năng của nhà cái.
2.	Ngưỡng Rủi Ro Là Trần Cố Định (Risk Threshold is a Fixed Ceiling): Công ty xác định một mức lỗ tối đa có thể chấp nhận cho mỗi lựa chọn/sự kiện. Con số này là một giới hạn cứng, không thay đổi. Bất kỳ giao dịch nào có thể khiến tổng nợ tiềm tàng vượt qua giới hạn này đều phải bị ngăn chặn.
3.	Mục Tiêu Hệ Thống Là Phòng Ngừa (The System's Goal is Prevention): Chức năng cốt lõi của hệ thống là ngăn chặn bất kỳ giao dịch nào có thể khiến Tổng Nợ Tiềm Tàng vượt qua Trần Cố Định. Thay vì phản ứng sau khi rủi ro xảy ra, hệ thống chủ động ngăn chặn rủi ro ngay từ đầu.
Các giải pháp toàn diện
Cơ Chế Phân Quyền Xử Lý Rủi Ro Theo Vai Trò Nhà Cái
Để triển khai các quy tắc rủi ro khác nhau, lõi của Risk Management Service phải được xây dựng dựa trên cơ chế phân quyền theo vai trò của nhà cái. Luồng xử lý logic phải tuân thủ các bước sau:
1.	Xác Định Vai Trò Nhà Cái: Khi nhận một yêu cầu xử lý (tạo thị trường, chấp nhận cược), hệ thống phải xác định vai trò của nhà cái đang vận hành thị trường đó: platform_admin (gồm super_admin, admin) hoặc individual_bookmaker (gồm người dùng cá nhân, nhóm).
2.	Áp Dụng Quy Tắc Bắt Buộc:
o	Nếu vai trò là platform_admin, hệ thống sẽ bỏ qua mọi cài đặt tùy chỉnh và áp đặt các quy tắc an toàn mặc định: Biên lợi nhuận, Ngưỡng rủi ro tối đa, và Dynamic Odds luôn được kích hoạt.
3.	Áp Dụng Quy Tắc Dựa Trên Lựa Chọn:
•	Nếu vai trò là individual_bookmaker, hệ thống sẽ dựa vào lựa chọn mà người dùng đã thực hiện trong quy trình "Buộc Phải Lựa Chọn" để áp dụng quy tắc.
•	Xử lý logic theo lựa chọn:
o	Nếu người dùng đã chọn "Kích hoạt bảo vệ tự động", Risk Management Service sẽ áp đặt việc sử dụng Dynamic Odds và yêu cầu một Ngưỡng Rủi Ro Tối Đa hợp lệ.
o	Nếu người dùng đã chọn "Tự quản lý rủi ro thủ công" và hoàn thành xác nhận, Risk Management Service sẽ vận hành theo các quy tắc mặc định rủi ro cao: không kích hoạt Dynamic Odds và coi toàn bộ vốn là Ngưỡng Rủi Ro.
•	Kiểm tra trạng thái lựa chọn: Hệ thống sẽ không xử lý bất kỳ yêu cầu tạo thị trường nào từ individual_bookmaker nếu trạng thái lựa chọn phương thức quản lý rủi ro chưa được ghi nhận.

Quản Lý Trách Nhiệm Chi Trả (Liability Management)
Đây là nguyên tắc vàng và quan trọng nhất. Thay vì theo dõi "còn bao nhiêu phiếu", hệ thống phải liên tục theo dõi và kiểm soát "Trách Nhiệm Chi Trả" cho từng kết quả, cho N lựa chọn mà nhà cái phải trả bao nhiêu tiền. Mục tiêu không phải là bán hết 1.000 phiếu, mà là "quản lý dòng tiền và cân bằng rủi ro để đảm bảo lợi nhuận trong mọi kịch bản". Người dùng cá nhân, nhóm người dùng hoặc "admin do super admin của hệ thống chỉ định" phải đặt ra một ngưỡng rủi ro tối đa cho mỗi kết quả của trận đấu.
Công thức tính Trách nhiệm RÒNG: Trách nhiệm RÒNG nếu "Kết quả X" xảy ra = (Tổng Payout nếu X xảy ra bao gồm cả PROMOTION) - (Tổng Tiền Cược vào TẤT CẢ CÁC KẾT QUẢ CÒN LẠI)
Ví dụ với cược Thắng-Hòa-Thua:
•	Trách nhiệm nếu "Hòa" = (Tổng Payout nếu "Hòa") - (Tổng Cược "Thắng" + Tổng Cược "Thua")
•	Và tương tự cho các cửa còn lại.
Với cược tỷ số, hệ thống sẽ phải tính toán đồng thời trách nhiệm cho từng tỷ số (ví dụ: "1-0", "1-1", "2-1", v.v.).
Cách hoạt động: Hệ thống không theo dõi "còn bao nhiêu phiếu", mà liên tục tính toán. Mỗi khi một phiếu cược được bán, hệ thống phải lưu lại không chỉ số tiền cược mà còn cả tỷ lệ cược tại đúng thời điểm đó.
Ví dụ về dữ liệu hệ thống cần lưu:
ID Phiếu	Cửa Cược	Tiền Cược	Tỷ Lệ Lúc Cược	Tiền Thưởng Tiềm Năng
001	Barcelona	$20	2.40	$48.00
002	Real Madrid	$20	1.85	$37.00
003	Barcelona	$20	2.25	$45.00
004	Barcelona	$20	2.10	$42.00
...	...	...	...	...









Từ đó, hệ thống tính toán:
•	Tổng tiền đã cược cho Real Madrid (Stake_RM)
•	Tổng tiền đã cược cho Barcelona (Stake_Barca)
•	Trách nhiệm RÒNG nếu Real thắng: (Tổng Payout nếu Real thắng là Tổng Tiền Thưởng Tiềm Năng của tất cả các phiếu cược cho Real) - (Tổng Cược đã cược cho Barca)
•	Trách nhiệm RÒNG nếu Barca thắng: (Tổng Payout nếu Barca thắng là Tổng Tiền Thưởng Tiềm Năng của tất cả các phiếu cược cho Barca) - (Tổng Cược đã cược cho Real)
Trụ cột 1: Thiết Lập Biên Lợi Nhuận Nhà Cái (Vigorish/Margin)
Đây là lớp phòng thủ tài chính đầu tiên, đảm bảo rằng ngay cả khi sổ cược cân bằng, nhà cái vẫn có lợi nhuận lý thuyết. Đây là điều kiện cần để kinh doanh bền vững. Một tỷ lệ cược chuyên nghiệp phải được thiết lập sao cho tổng xác suất nghịch đảo của chúng luôn lớn hơn 100% (ví dụ: 104% - 108%). Khoản chênh lệch đó chính là lợi nhuận đảm bảo của nhà cái.
Ví dụ: Nếu tỷ lệ cược là 1.90 - 1.90:
•	Tổng xác suất: (1/1.90) + (1/1.90) = 52.63% + 52.63% = 105.26%
•	Biên lợi nhuận (margin) của nhà cái là 5.26%.
Nếu tiền cược được chia đều cho 2 cửa, nhà cái chắc chắn có lãi 5.26% tổng số tiền cược, bất kể kết quả.
Trụ cột 2: Hệ Thống Tự Động Điều Chỉnh Tỷ Lệ Cược Linh Hoạt (Dynamic Odds) (Phòng Thủ Chủ Động)
Đây là công cụ chính để chủ động cân bằng rủi ro. Bằng cách thay đổi tỷ lệ cược theo thời gian thực dựa trên dòng tiền, hệ thống nỗ lực giữ cho Tổng Nợ của mỗi lựa chọn không tiến quá nhanh về phía Trần Cố Định. Đây chính là cơ chế tự động hóa giúp nhà cái tồn tại và phát triển, biến một hoạt động có vẻ may rủi thành một bài toán quản trị rủi ro và tối ưu hóa lợi nhuận dựa trên dữ liệu thời gian thực.
Nó hoạt động theo một vòng lặp hoàn hảo: Nhận cược → Tính toán Trách nhiệm chi trả → So sánh với Ngưỡng rủi ro → Nếu bằng hoặc gần bằng ngưỡng trách nhiệm chi trả thì tạo ra Tỷ lệ cược mới an toàn hơn không để vượt ngưỡng trách nhiệm chi trả nhưng vẫn đảm bảo lợi nhuận → Lặp lại.
Cơ chế: Khi tiền cược đổ dồn vào một cửa (ví dụ: Barca), hệ thống sẽ tự động điều chỉnh tỷ lệ cược:
•	Hạ tỷ lệ cược của cửa đó (ví dụ: Barca từ 2.4 xuống thấp hơn) để làm nó giảm sức hấp dẫn hơn.
•	Tăng tỷ lệ cược của cửa còn lại (ví dụ: Real từ 1.85 lên cao hơn) để thu hút người chơi đặt cược vào đó, nhằm cân bằng lại rủi ro.
Mục tiêu: Khuyến khích người chơi đặt cược vào cửa ít được ưa chuộng hơn, từ đó tự động cân bằng lại rủi ro cho nhà cái. Giữ cho sổ cược cân bằng nhất có thể mà không cần can thiệp "cứng".
Lưu ý về phạm vi áp dụng trong Giai đoạn MVP: Với việc sử dụng The Odds API làm nguồn cung cấp tỷ lệ cược tham khảo, cơ chế "Dynamic Odds" trong giai đoạn đầu sẽ tập trung vào việc cân bằng rủi ro nội bộ. Nghĩa là, hệ thống sẽ điều chỉnh tỷ lệ cược chủ yếu dựa trên dòng tiền người dùng đặt vào các cửa trên chính nền tảng của bạn, nhằm đảm bảo sổ cược được cân bằng. Việc điều chỉnh tỷ lệ cược theo biến động của thị trường toàn cầu theo từng giây sẽ được xem xét ở các giai đoạn sau.
Trụ cột 3: Ngưỡng Rủi Ro Tối Đa và Khóa Thị Trường Tự Động (Phanh Khẩn Cấp)
Đây là lớp phòng thủ "cứng tuyệt đối" cuối cùng, hoạt động như một chiếc phanh khẩn cấp, để ngăn chặn thảm họa. Khi một giao dịch sắp khiến Tổng Nợ vượt Trần Cố Định, cơ chế này sẽ được kích hoạt để từ chối giao dịch đó.
Đặt Ngưỡng Rủi Ro Tối Đa Là Trần Cố Định (Risk Threshold is a Fixed Ceiling): Xác định một mức lỗ tối đa được áp dụng cho từng lựa chọn riêng lẻ, cho bất kỳ kết quả nào cho mỗi lựa chọn/sự kiện. Con số này là một giới hạn cứng, không thay đổi. Mục tiêu là ngăn chặn bất kỳ giao dịch nào có thể khiến Tổng Nợ Tiềm Tàng vượt qua Trần Cố Định mà người dùng cá nhân, nhóm người dùng và "admin do super admin của hệ thống chỉ định" thiết lập (ví dụ: $2,000).
Trần Cố Định cho trận đấu là sự kết hợp giữa Trần Cố Định CHÍNH và Trần Cố Định PHỤ.
•	Nếu một người chơi đặt cược vào một lựa chọn thông thường (ví dụ: cược tỷ số 1-1), khoản Nợ phát sinh sẽ được tính vào và so sánh với Trần Cố Định CHÍNH (ví dụ: $100,000).
•	Nếu một người chơi đặt cược dựa vào chương trình của Hệ Thống Khuyến Mãi (Promotion System) (ví dụ như: "Bonus Odds / Odds Boost (Tăng Tỷ Lệ), Free Bet (Cược Miễn Phí), Gift Money / Bonus Credits (Tặng Tiền), Cashback Percentage (Hoàn Tiền)"), khoản Nợ phát sinh sẽ được tính vào và so sánh với Trần Cố Định PHỤ (ví dụ: $5,000).
•	Trần Cố Định CHÍNH luôn lớn hơn Trần Cố Định PHỤ.
•	Các chương trình Khuyến mãi được quản lý bởi một Trần Cố Định phụ, nhỏ hơn và nghiêm ngặt hơn, nhưng vẫn tuân thủ nguyên tắc chung.
Hành Động Khóa Thị Trường:
•	Điều kiện: Khi dòng tiền cực đoan vẫn tiếp tục đổ vào một cửa bất chấp tỷ lệ đã bị hạ, khiến cho Trách Nhiệm Là Nợ Phải Trả tiến sát hoặc bằng Ngưỡng Rủi Ro Tối Đa.
•	Tính Tổng Nợ Tiềm Tàng: Hệ thống thực hiện phép tính Tổng Nợ Mới Tiềm Tàng = Tổng Nợ Hiện Tại + Nợ Mới.
•	So Sánh và Quyết Định: Hệ thống so sánh Tổng Nợ Mới Tiềm Tàng với Trần Cố Định.
•	Hành Động Phòng Ngừa:
o	Nếu Tổng Nợ Mới Tiềm Tàng ≤ Trần Cố Định → Giao dịch được chấp thuận.
o	Nếu Tổng Nợ Mới Tiềm Tàng > Trần Cố Định → Giao dịch bị từ chối.
•	Hành động: Hệ thống sẽ tự động TẠM KHÓA (đóng) việc nhận cược cho cửa đó . Lựa chọn này sẽ bị vô hiệu hóa trên giao diện người dùng. Người chơi vẫn có thể đặt cược cho các cửa khác miễn là trách nhiệm của chúng vẫn nằm trong vùng an toàn khả thi.
•	Mục tiêu: Đảm bảo nhà cái không bao giờ phải đối mặt với một khoản lỗ vượt quá khả năng chi trả.
Tích Hợp và Quản Lý Rủi Ro cho Hệ Thống Khuyến Mãi (Promotions)
Hệ thống Khuyến mãi không phải là yếu tố bên lề mà là một biến số tài chính có tác động trực tiếp và sâu sắc đến rủi ro. Mỗi chương trình khuyến mãi đều làm thay đổi phương trình lợi nhuận.
•	Bonus Odds (Tăng Tỷ Lệ): Đây là loại nguy hiểm nhất, trực tiếp làm tăng vọt Payout tiềm năng. Giải pháp là phải kiểm soát các thị trường này bằng một 
ngưỡng rủi ro phụ, riêng biệt và thấp hơn nhiều.
•	Free Bet (Cược Miễn Phí): Tạo ra một "trách nhiệm ảo" không được bù đắp bằng tiền cược thật. Hệ thống phải cộng phần 
tiền thắng ròng (Winnings) vào tổng trách nhiệm của kết quả đó.
•	Gift Money (Tặng Tiền): Khi người chơi dùng tiền thưởng để cược, nó hoạt động như một lượt cược bằng tiền thật và bắt buộc phải được tính vào tổng trách nhiệm chi trả.
•	Cashback (Hoàn Tiền): Tác động gián tiếp, làm giảm Lợi Nhuận Gộp Thực Tế. Cần được tính trước khi thiết lập biên lợi nhuận ban đầu.
Để quản lý tổng thể, Hệ thống Quản lý Rủi ro và Hệ thống Khuyến mãi phải được 
tích hợp chặt chẽ, cho phép tạo ra các ngưỡng rủi ro phụ cho từng chiến dịch.
Mở Rộng Hệ Thống cho Cá Cược Trực Tiếp (In-Play)
Cá cược trong trận đòi hỏi hệ thống phải tính toán lại rủi ro sau mỗi giao dịch và sau mỗi sự kiện quan trọng trong trận đấu (bàn thắng, thẻ phạt, hết hiệp...).
•	Hai loại tỷ lệ cược:
o	Tỷ Lệ Cược Lý Thuyết: Dựa trên xác suất toán học thuần túy tại một thời điểm (ví dụ: xác suất tỷ số 1-0 ở phút 85).
o	Tỷ Lệ Cược Chào Bán: Là Tỷ lệ cược lý thuyết đã được điều chỉnh dựa trên Trách Nhiệm Ròng hiện tại của nhà cái. Đây là chìa khóa để quản lý rủi ro trong trận.
•	Cơ chế hoạt động: Hệ thống liên tục tính toán lại xác suất, đối chiếu với trách nhiệm tài chính, và điều chỉnh Tỷ lệ cược chào bán để điều hướng dòng tiền về phía an toàn, đảm bảo không kết quả nào vượt Trần Cố Định. Khi một kết quả gần như chắc chắn xảy ra (ví dụ tỷ số 3-0 ở phút 80), hệ thống sẽ tự động giảm tỷ lệ về gần 1.0 và cuối cùng là khóa cửa đó lại.
•	Lưu ý quan trọng cho Giai đoạn MVP:
Việc triển khai một hệ thống cá cược trong trận (in-play) với tỷ lệ cược tự động điều chỉnh theo từng sự kiện nhỏ trong trận đấu (bàn thắng, thẻ phạt, ...) đòi hỏi một nguồn dữ liệu có độ trễ cực thấp (low-latency) từ các nhà cung cấp cao cấp (Tier 1). Do đó, trong Giai đoạn 1 (MVP) sử dụng API từ The Odds API và API-Sports.io, tính năng "Cá cược trong trận" sẽ được triển khai ở mức độ cơ bản. Cụ thể:
o	Người dùng có thể đặt cược cho các kết quả cuối cùng (ví dụ: đội thắng, tổng số bàn thắng) trong khi trận đấu đang diễn ra.
o	Tỷ lệ cược sẽ được cập nhật định kỳ theo tần suất làm mới của API (ví dụ: mỗi 5-15 phút), thay vì thay đổi theo từng giây. Mô hình tính toán phức tạp dựa trên Phân phối Poisson sẽ được xem xét triển khai trong Giai đoạn 2 khi nền tảng tích hợp các nguồn dữ liệu cao cấp hơn.

Mô Hình Toán Học và Thuật Toán Triển Khai
Để hiện thực hóa các lớp phòng thủ trên, hệ thống cần dựa trên các mô hình toán học và thuật toán cụ thể.
•	Mô Hình 1: Tính Xác Suất Lý Thuyết (Ví dụ: Phân phối Poisson cho bóng đá)
o	Đầu vào: Số bàn thắng kỳ vọng (Expected Goals - λ) của mỗi đội, được điều chỉnh theo thời gian còn lại của trận đấu.
o	Công thức Poisson: P(k;λ) = (e^-λ * λ^k) / k! được dùng để tính xác suất một đội ghi được k bàn thắng.
o	Kết hợp: Bằng cách nhân xác suất Poisson của mỗi đội, ta có thể tính ra xác suất cho một tỷ số cuối cùng cụ thể. Từ đó suy ra Tỷ lệ cược lý thuyết (1 / Xác suất).
•	Mô Hình 2: Tính Tỷ Lệ Cược Chào Bán (Risk-Adjusted Offered Odds)
o	Đây là công thức cốt lõi, kết hợp xác suất lý thuyết với tình hình tài chính thực tế.
o	Công thức hoàn chỉnh: 
	Odds_chào_bán = (Odds_lý_thuyết / M) * (1 - (L_ròng / T_cố_định)) 
o	Diễn giải:
	M là biên lợi nhuận mong muốn (ví dụ: 1.05).
	Khi rủi ro cao (L_ròng > 0), hệ số (1 - ...) sẽ nhỏ hơn 1, làm giảm tỷ lệ cược chào bán.
	Khi an toàn (L_ròng < 0), hệ số (1 - ...) sẽ lớn hơn 1, làm tăng tỷ lệ cược chào bán để thu hút dòng tiền.
	Nếu công thức cho ra kết quả ≤ 1.0, hệ thống sẽ khóa thị trường đó lại.
Luồng Hoạt Động Thực Tế Khi Có Sự Kiện Trong Trận
Khi một sự kiện quan trọng xảy ra (ví dụ: một bàn thắng được ghi), hệ thống sẽ:
1.	Lọc và Vô hiệu hóa: Ngay lập tức vô hiệu hóa tất cả các kết quả không thể xảy ra được nữa (ví dụ: tỷ số 0-0 sau khi có bàn thắng).
2.	"Bộ não Xác suất" hoạt động: Gọi Mô hình 1 (Poisson) để tính toán lại Tỷ lệ cược Lý thuyết mới cho những kết quả còn khả thi.
3.	"Bộ não Quản trị Rủi ro" hoạt động: Chuyển Tỷ lệ cược Lý thuyết sang Mô hình 2 để tính toán và đưa ra Tỷ lệ cược Chào bán cuối cùng, đã điều chỉnh theo rủi ro.
4.	Hiển thị cho người dùng: Cập nhật giao diện cá cược với các lựa chọn và tỷ lệ cược mới.
Sơ đồ quy trình vận hành kết hợp và công thức tính toán hoàn thiện
Quy trình vận hành của hệ thống quản lý rủi ro là một vòng lặp liên tục, đảm bảo sự cân bằng và lợi nhuận:
Bước 1: Thiết Lập Ban Đầu
•	Xác định biên lợi nhuận mong muốn (ví dụ: 5%). (Chỉ áp dụng bắt buộc cho nhà cái là super admin và admin do super admin của hệ thống chỉ định, còn nhà cái là người dùng cá nhân hoặc nhóm người dùng thì không áp dụng).
•	Hệ thống hỗ trợ đặt ra tỷ lệ cược ban đầu dựa trên biên lợi nhuận đó (ví dụ: 1.95 - 1.95). (Chỉ áp dụng cho nhà cái là super admin và admin do super admin của hệ thống chỉ định, còn nhà cái là người dùng cá nhân hoặc nhóm người dùng thì bắt buộc phải tự thiết lập).
•	Đặt ra Ngưỡng Rủi Ro Tối Đa (ví dụ: lỗ không quá $2,000). (Chỉ áp dụng bắt buộc cho nhà cái là super admin và admin do super admin của hệ thống chỉ định, còn nhà cái là người dùng cá nhân hoặc nhóm người dùng thì không bắt buộc, mặc định thiết lập Ngưỡng Rủi Ro Tối Đa bằng toàn bộ số vốn bỏ ra cho sự kiện và họ được phép tự thiết lập thủ công).
Bước 2: Mở Cược, Tiếp Nhận và Ghi Nhận Giao Dịch
•	Hệ thống bắt đầu nhận cược và liên tục tính toán Trách Nhiệm Chi Trả cho mỗi cửa sau mỗi giao dịch.
•	Trần Cố Định ≥ Trách nhiệm chi trả = (Tổng Payout vào một cửa là Tổng Tiền Thưởng Tiềm Năng của tất cả các phiếu cược cho cửa đó (Trần Cố Định CHÍNH)) + (tổng chi trả tiềm năng cho chương trình Khuyến Mãi Promotion được sử dụng cho cửa được chọn (Trần Cố Định PHỤ)) - Tiền cược vào cửa còn lại.
•	Quan trọng: Với mỗi phiếu cược được bán, hệ thống phải ghi nhận chi tiết: ID giao dịch, Số tiền cược, Cửa đã chọn, và Tỷ lệ cược tại đúng thời điểm giao dịch.
Bước 3: Vòng Lặp Tự Điều Chỉnh Quản Trị Rủi Ro (Liên tục) (Giải pháp Cấp 1)
•	Sau mỗi giao dịch, hệ thống tính toán lại Trách Nhiệm Chi Trả Ròng Chính Xác.
•	Công Thức Tính Trách Nhiệm Chính Xác (Khi có Dynamic Odds):
•	Tính Tổng Tiền Thưởng Tiềm Năng (Total Payout Liability bao gồm Promotion) cho mỗi cửa:
o	Hệ thống quét toàn bộ giao dịch đã ghi nhận.
o	Tổng Payout (Cửa được chọn) = Σ (Tiền Cược của từng phiếu A × Tỷ Lệ Cược của cửa được chọn theo từng thời điểm khớp lệnh xác định) + Σ (Tiền chi trả tiềm năng cho chương trình Khuyến Mãi (Promotion) được sử dụng cho cửa được chọn theo từng thời điểm khớp lệnh xác định).
o	Tổng Payout (các Cửa còn lại) = Σ (Tiền Cược của từng phiếu B × Tỷ Lệ Cược của các cửa còn lại theo từng thời điểm khớp lệnh xác định) + Σ (Tiền chi trả tiềm năng cho chương trình (Promotion) được sử dụng cho các cửa còn lại theo từng thời điểm khớp lệnh xác định).
•	Tính Trách Nhiệm Ròng (Net Liability) Cuối Cùng:
o	Trách nhiệm RÒNG nếu Cửa được chọn thắng = Tổng Payout (Cửa được chọn) - Tổng Cược (các Cửa còn lại không bao gồm các Promotions).
•	Hệ thống liên tục sử dụng cơ chế điều chỉnh tỷ lệ cược tự động để khuyến khích dòng tiền chảy theo hướng cân bằng, giữ cho rủi ro luôn ở mức thấp (chỉ áp dụng bắt buộc cho nhà cái là super admin và admin do super admin của hệ thống chỉ định, còn nhà cái là người dùng cá nhân hoặc nhóm người dùng thì hệ thống sẽ để mặc định là tắt và có thể tắt/mở theo ý thích).
Bước 4: Kích Hoạt Phanh Khẩn Cấp (Giải pháp Cấp 2)
•	Trong trường hợp dòng tiền quá bất thường và cực đoan, nếu Trách Nhiệm Chi Trả chạm đến Ngưỡng Rủi Ro Tối Đa (ví dụ: $2,000), và khi một giao dịch sắp khiến Tổng Nợ vượt Trần Cố Định, cơ chế này sẽ được kích hoạt để từ chối giao dịch đó. Hệ thống sẽ ngay lập tức khóa nhận cược cho cửa có rủi ro cao.
Bước 5: Tổng Kết - Mô Hình Kinh Doanh Bền Vững
•	Bằng cách chuyển đổi từ một mô hình bán hàng tĩnh, mong manh sang một hệ thống quản trị rủi ro tài chính đa tầng của nhà cái được kiểm soát tuyệt đối, năng động và chính xác, nhà cái đã loại bỏ hoàn toàn nguy cơ thua lỗ thảm họa và đảm bảo lợi nhuận bền vững.
Kết Luận và Hướng Phát Triển
Dự án nền tảng cá cược thể thao này đã được thiết kế với một kiến trúc module hóa mạnh mẽ, tích hợp các thành phần cốt lõi như hệ thống xác thực người dùng (Auth), ứng dụng cá cược (Betting), module dữ liệu thể thao và đặc biệt là module quản lý rủi ro tài chính tiên tiến. Sự kết hợp này không chỉ mang lại trải nghiệm cá cược đa dạng và an toàn cho người dùng mà còn đảm bảo sự bền vững và lợi nhuận cho nhà cái thông qua các cơ chế kiểm soát rủi ro chủ động và linh hoạt.
Với việc áp dụng các nguyên tắc quản lý trách nhiệm chi trả, thiết lập biên lợi nhuận, điều chỉnh tỷ lệ cược động và cơ chế phanh khẩn cấp, hệ thống đã chuyển đổi mô hình kinh doanh cá cược từ một hoạt động tiềm ẩn rủi ro lớn thành một bài toán quản trị tài chính được kiểm soát chặt chẽ. Điều này giúp nhà cái loại bỏ nguy cơ thua lỗ thảm họa và tối ưu hóa lợi nhuận trong mọi kịch bản thị trường.
Về Sự Phức Tạp của Vai Trò "Nhà Cái Cá Nhân"
Tài liệu đã đề cập đến việc hệ thống cho phép người dùng cá nhân/nhóm người dùng hoạt động như một nhà cái, với các tùy chọn tắt/mở các cơ chế quản lý rủi ro. Đây là một tính năng nâng cao và có độ phức tạp rất lớn. Để đảm bảo sự thành công của dự án, chúng tôi đề xuất phân tách theo lộ trình phát triển sau:
•	Giai đoạn 1 (Sản phẩm khả dụng tối thiểu - MVP):
o	Hệ thống sẽ chỉ hoạt động với một mô hình duy nhất: Nền tảng (do super_admin và admin quản lý) là nhà cái trung tâm.
o	Tất cả các cơ chế quản lý rủi ro (Dynamic Odds, Ngưỡng Rủi Ro) là bắt buộc và được áp dụng trên toàn hệ thống.
o	Mục tiêu của giai đoạn này là xây dựng và kiểm chứng sự ổn định, an toàn và hiệu quả của lõi quản lý rủi ro.
o	Tích hợp thành công với các API bên ngoài là API-Sports.io và The-Odds-API.com để làm nguồn cung cấp dữ liệu đầu vào cho toàn hệ thống, kiểm chứng khả năng thu thập và xử lý dữ liệu tự động.
•	Giai đoạn 2 (Hướng phát triển tương lai):
o	Khi phát triển tính năng "Nhà Cái Cá Nhân", trọng tâm sẽ là triển khai cơ chế "Buộc Phải Lựa Chọn" một cách an toàn và hiệu quả.
	Dự án con này sẽ phải ưu tiên thiết kế một quy trình tạo sự kiện chặt chẽ, trong đó người dùng không thể tiếp tục nếu chưa đưa ra lựa chọn rõ ràng về phương thức quản lý rủi ro.
	Lõi Risk Management Service sẽ được nâng cấp để xử lý logic phân quyền dựa trên lựa chọn đã được người dùng xác nhận, thay vì dựa vào các thiết lập mặc định có thể gây hiểu lầm.
Cách tiếp cận này giúp giảm thiểu rủi ro trong giai đoạn đầu và tập trung nguồn lực để hoàn thiện tính năng cốt lõi quan trọng nhất của sản phẩm.

Hướng phát triển trong tương lai: Để tiếp tục nâng cao giá trị và khả năng cạnh tranh của nền tảng, một số hướng phát triển tiềm năng có thể được xem xét:
•	Mở rộng sang các loại hình cá cược khác: Ngoài thể thao, có thể mở rộng sang các loại hình cá cược khác như casino trực tuyến, xổ số, hoặc các trò chơi ảo.
•	Phân tích dữ liệu nâng cao: Xây dựng các công cụ phân tích dữ liệu mạnh mẽ hơn để cung cấp cái nhìn sâu sắc về hành vi người dùng, hiệu suất thị trường, và các chỉ số rủi ro, hỗ trợ ra quyết định chiến lược.
•	Tối ưu hóa hiệu suất và khả năng mở rộng: Liên tục cải thiện kiến trúc và công nghệ để đảm bảo hệ thống có thể xử lý lượng lớn giao dịch và người dùng đồng thời, đặc biệt trong các sự kiện thể thao lớn.
•	Cải thiện trải nghiệm người dùng: Phát triển các tính năng tương tác mới, giao diện người dùng trực quan hơn, và hỗ trợ đa ngôn ngữ để thu hút và giữ chân người dùng.
•	Hỗ trợ Đa nền tảng: Được thiết kế để hoạt động liền mạch trên cả ứng dụng web và mobile, cung cấp API thống nhất cho các giao diện người dùng khác nhau.
Với nền tảng vững chắc đã được thiết kế, dự án này có tiềm năng lớn để trở thành một trong những nền tảng cá cược thể thao hàng đầu, mang lại giá trị vượt trội cho cả người chơi và nhà cái

Phụ Lục: Các Sơ Đồ Kiến Trúc và Luồng Dữ Liệu
Phụ lục này bổ sung các sơ đồ trực quan hóa để làm rõ hơn kiến trúc và các luồng hoạt động đã được mô tả trong tài liệu.
1. Sơ Đồ Kiến Trúc Tổng Thể (Microservices)
Biểu đồ này minh họa kiến trúc microservices của hệ thống, cho thấy sự tương tác giữa các thành phần chính.
•	Luồng yêu cầu từ người dùng:
1.	Người dùng cuối (Người chơi, Admin) tương tác với Tầng Presentation (Betting App, Admin Panel).
2.	Mọi yêu cầu từ tầng Presentation được gửi đến một điểm truy cập duy nhất là API Gateway.
3.	API Gateway chịu trách nhiệm xác thực cơ bản, sau đó định tuyến yêu cầu đến các service nghiệp vụ phù hợp ở Tầng Business Logic.
•	Tương tác giữa các Service:
o	Auth Service: Xử lý tất cả các yêu cầu liên quan đến đăng ký, đăng nhập và phân quyền.
o	Betting Service: Xử lý logic đặt cược, tính toán kết quả và thanh toán. Service này tương tác với Risk Management Service để kiểm tra tính hợp lệ của cược.
o	Risk Management Service: Tính toán rủi ro, điều chỉnh tỷ lệ cược động và quản lý trách nhiệm chi trả.
o	Sports Data Service: Cung cấp dữ liệu về các sự kiện, giải đấu và tỷ lệ cược ban đầu cho các service khác.
•	Giao tiếp bất đồng bộ:
o	Các service giao tiếp với nhau qua Message Queue (MQ) cho các tác vụ không cần phản hồi ngay lập tức. Ví dụ, Betting Service gửi thông báo nhận được một lô dữ liệu mới về một cược mới qua MQ, nó có thể đưa thông tin này vào một hàng đợi để Risk Management Service cập nhật lại trách nhiệm chi trả và các service khác sẽ lắng nghe hàng đợi này và xử lý dữ liệu mà không làm chậm trễ quá trình thu thập dữ liệu gốc và không làm chậm giao dịch của người dùng. Điều này giúp quá trình "nạp" dữ liệu từ API bên ngoài diễn ra trơn tru và độc lập, không bị tắc nghẽn bởi các yêu cầu xử lý tức thời, đảm bảo luồng dữ liệu hiệu quả và tiết kiệm.
•	Tầng dữ liệu:
o	Mỗi service có cơ sở dữ liệu riêng (User DB, Transaction DB, Risk DB, Sports DB) để đảm bảo tính độc lập và khả năng mở rộng.
2. Sơ Đồ Luồng Dữ Liệu: Đặt Cược
Biểu đồ này minh họa chi tiết các bước khi người dùng thực hiện một giao dịch đặt cược.
1.	Người dùng (trên Betting App): Chọn sự kiện và loại cược. Giao diện hiển thị tỷ lệ cược được lấy trực tiếp từ Risk Management Service.
2.	Betting App -> Betting Service: Người dùng nhập số tiền và xác nhận cược. Yêu cầu được gửi đến Betting Service.
3.	Betting Service -> Risk Management Service: Yêu cầu được chuyển tiếp đến Risk Management Service để kiểm tra rủi ro.
4.	Risk Management Service (Kiểm tra rủi ro):
o	Tính toán trách nhiệm chi trả tiềm năng mới nếu cược được chấp nhận.
o	So sánh trách nhiệm này với "Ngưỡng Rủi Ro Tối Đa" đã được lưu trong Risk Database.
o	Nếu vượt ngưỡng, từ chối giao dịch. Nếu không, chấp thuận.
5.	Risk Management Service -> Betting Service: Gửi lại kết quả (chấp nhận/từ chối).
6.	Betting Service (Xử lý kết quả):
o	Nếu cược được chấp nhận, ghi giao dịch vào Transaction Database và cập nhật số dư người dùng.
o	Gửi thông báo đến Message Queue để Risk Management Service cập nhật lại tổng trách nhiệm chi trả một cách bất đồng bộ.
7.	Betting Service -> Betting App: Thông báo kết quả (thành công/thất bại) cho người dùng.
3. Sơ Đồ Quy Trình Vòng Lặp Quản Lý Rủi Ro
Biểu đồ này mô tả vòng lặp hoạt động liên tục của Module Quản Lý Rủi Ro.
1.	Thiết lập ban đầu: Nhà cái đặt ra Biên lợi nhuận (Margin) và Ngưỡng Rủi Ro Tối Đa (Trần Cố Định).
2.	Nhận yêu cầu cược: Hệ thống nhận một yêu cầu đặt cược mới từ Betting Service.
3.	Tính toán rủi ro tiềm năng: Hệ thống tính toán: Tổng Nợ Mới Tiềm Tàng = Tổng Nợ Hiện Tại + Nợ Mới từ cược đang xét.
4.	So sánh Quyết định (Kích hoạt Phanh Khẩn Cấp): 
o	Hệ thống so sánh Tổng Nợ Mới Tiềm Tàng với Trần Cố Định.
o	Nếu Tổng Nợ Mới Tiềm Tàng > Trần Cố Định: Giao dịch bị từ chối. Hệ thống có thể khóa thị trường (đóng nhận cược) cho lựa chọn đó để ngăn chặn thua lỗ thảm họa.
o	Nếu Tổng Nợ Mới Tiềm Tàng ≤ Trần Cố Định: Giao dịch được chấp thuận.
5.	Cập nhật và điều chỉnh (Nếu cược được chấp nhận):
o	Ghi nhận giao dịch và cập nhật Trách Nhiệm Chi Trả Ròng.
o	Kích hoạt thuật toán Dynamic Odds: Tự động điều chỉnh lại tỷ lệ cược dựa trên dòng tiền mới để cân bằng lại rủi ro, khuyến khích người chơi đặt vào các cửa khác.
6.	Lặp lại: Hệ thống quay trở lại Bước 2, liên tục theo dõi và điều chỉnh theo thời gian thực.
