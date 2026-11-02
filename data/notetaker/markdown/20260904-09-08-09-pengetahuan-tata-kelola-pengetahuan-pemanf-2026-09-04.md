# 20260904-09.08.09 [Pengetahuan Tata Kelola Pengetahuan, Pemanfaatan Teknologi, dan Sosialisasi Layanan Kedeputian PMP x UGM]

**Source:** Web · Tab  
**Started:** 4/9/2026, 09.08.09  
**Duration:** 126m 35s

## Summary

## Ringkasan

Pertemuan ini merupakan kunjungan studi (benchmarking) dari tim Kedeputian Perencanaan Makro Bappenas (Sesdep PMP) ke Biro Transformasi Digital Universitas Gadjah Mada (UGM) untuk mempelajari pemanfaatan teknologi digital dan kecerdasan buatan. Pak Yunus beserta tim Bappenas memaparkan tantangan berupa silo data antar direktorat, aset digital yang belum terintegrasi, serta rencana pengembangan "Makrointelligence Hub" sebagai repositori pengetahuan terpadu berbasis RAG (*Retrieval-Augmented Generation*). Grady mendemonstrasikan Portal PMP yang telah dilengkapi agen AI berbasis semantik untuk pencarian dokumen dan analisis. Dari sisi UGM, Mardhani dan tim (Alif, Dedi Eko, Pak Farda) memaparkan visi *Intelligent University*, penataan ulang arsitektur enterprise, strategi pemetaan data, serta berbagai use case seperti analitik dampak, pemetaan bencana, dan *agentic AI*. Kedua belah pihak sepakat menjalin kolaborasi lanjutan untuk pengembangan platform AI di lingkungan pemerintahan.

## Keputusan Penting

- Bappenas (Sesdep PMP) akan mengembangkan **Makrointelligence Hub** berisi repositori pengetahuan, agen AI berbasis RAG, dan integrasi dashboard antar unit kerja eselon dua di bawah Kedeputian Perencanaan Makro.
- UGM merekomendasikan pendekatan **"baby step"** dan **"working with example"**: mulai dari solusi sederhana yang konkret, bukan langsung membangun sistem besar.
- Untuk tahap awal, Bappenas akan memfokuskan pada data internal (tidak mengambil sumber eksternal) guna menghindari risiko keamanan; penggunaan model AI asal Tiongkok ditunda karena belum ada kebijakan *zero data retention*.
- UGM mendorong pengembangan **data model berbahasa Indonesia** (merujuk pengalaman Sahabat AI bersama Indosat) agar konteks dan nuansa bahasa lebih akurat.
- Bappenas akan mengoordinasikan kebutuhan infrastruktur digital (server, *token* langganan AI) bersama Pusdatin dan mengadvokasi pengaturan anggaran untuk teknologi AI di sektor pemerintah.
- Akan dibentuk **WAG (WhatsApp Group)** khusus antara tim Bappenas dan Biro Transdig UGM untuk komunikasi dan tindak lanjut teknis.

## Daftar Tindak Lanjut

- **Grady (Sesdep PMP):** Menindaklanjuti perbaikan Portal PMP — menghubungkan agen RAG ke dashboard EWS (*Early Warning System*) dan memastikan seluruh dokumen masuk ke *server* internal.
- **Pak Yunus (Plt Kabag PMRU Sesdep PMP):** Menyusun konsep *Knowledge Management Center* ("Perpustakaan PMP") sebagai area repositori dan agen EA dalam portal Bappenas, serta berkoordinasi dengan Pusdatin terkait penyediaan *server* dan infrastruktur.
- **Pak Ewin (Sesdep PMP):** Mengoordinasikan diskusi lanjutan antara Sesdep PMP dan Pusdatin mengenai platform AI di level kementerian, serta menyusun *roadmap* pengembangan 1–5 tahun (termasuk analisis dampak/output direktorat).
- **Miftah (Direktorat Produktivitas):** Mengembangkan use case pengukuran dampak kebijakan berbasis analitik (bukan sekadar *by number*) bersama tim Sesdep PMP.
- **Tim Biro Transdig UGM (Mardhani, Alif, Dedi Eko):** Membagikan akses ke platform UGM (aiugm.as.id, DTS Lab, dsb.) dan memfasilitasi diskusi teknis lanjutan; membuka peluang kerja sama riset dan *pilot* agen AI untuk Bappenas.
- **Kedua tim:** Membentuk WAG untuk koordinasi pasca-pertemuan; menjadwalkan pertemuan lanjutan di Jakarta untuk pembahasan spesifik kebutuhan Bappenas (analisis naskah dinas, *media monitoring*, prediksi ekonomi berbasis *word of mouth*).

## Catatan Tambahan

- Pak Yunus dan tim Bappenas juga menyinggung kebutuhan akan kerangka etika/aturan penggunaan AI di sektor pemerintahan; UGM telah menyusun kode etik pemanfaatan AI di tingkat universitas.
- Isu administratif anggaran AI (*token*, langganan *platform*) di Bappenas masih belum mendapat persetujuan penuh dari Direktorat Jenderal Perbendaharaan; UGM diminta membantu menyuarakan pentingnya regulasi alokasi anggaran teknologi di sektor pemerintah.

## Transcript

**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (00:00): Pembangunan hilirisasi, produktivitas, dan lain-lain, kami hari ini seperti undangan yang dilayangkan oleh Pak Sisdep kepada Pak Karo. Kami mohon perkenan nanti kepada
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (00:10): Rekan-rekan di apa namanya, diruapa namanya transformasi digital dari UGM itu untuk?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (00:21): Apa namanya, kami ingin memperoleh pembelajaran, Pak, sama referensi bagaimana pemanfaatan dari teknologi digital serta kecerdasan buatan atau akal imitasi itu bisa dikembangkan menjadi satu?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (00:46): Kemudian kami juga ingin melihat bagaimana dimanfaatkan dalam artificial intelligence itu diimplementasikan dalam melaksanakan kegiatan sehari-hari serta dalam pengelolaan dan perkembangan dashboardnya, jadi mungkin.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (00:58): Sebagai bahan gambaran kepada Papa, ini rekan-rekan di kami, ada Tim Kepala Kelola. Ini Mas Fikri yang bersama saya, terus kemudian ada Tim Anggaran dan lain-lain. Ini bersama-sama mereka.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (01:10): Menyiapkan bahan bisa ditampilkan ya, Mas Pikrian?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (01:15): Jadi, ada beberapa direktorat di bawah Kedeputian Perencanaan Makro yang saat ini dalam bekerjanya masih agak silo, Pak. Taruh jadi kami.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (01:39): Pekerjaan tersebut saat ini itu masih tersebar di database dari masing-masing unit kerja tersebut, kemudian mereka mengembangkan model-model mereka sendiri.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (02:03): Sebetulnya kami di level unit kerja eselon satunya itu tidak bisa memanfaatkan pengetahuan yang disebar di unit kerja eselon dua di bawahnya. Yang sebetulnya kalau itu di
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (02:15): Disintesakan itu akan menjadi satu, apa namanya? Satu bekal bagi pimpinan di level eselon satunya untuk mengambil keputusan sejak.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (02:27): Karena lebih komprehensif, jadi misalnya kami diminta untuk melakukan analisis tentang produktivitas dan kemudian hilirisasi, karena mungkin sekarang kan isunya adalah.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (02:38): Hilirisasi, nah itu ada di dua direktorat terpisah. Direktorat yang mengurusi hilirisasi, mereka punya kajian-kajian hilirisasi, tapi direktorat pengurusi produk digital dia juga bikin kajian sendiri. Nah, pada saat Bapak
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (02:50): Deputinya atau pimpinannya itu akan menyampaikan laporan kepada Bapak Menteri. Itu menjadi bahannya itu seperti kue lapis, Pak, jadi ditumpuk gitu, produktivitas di atas, sederhanisasi di bawah.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (03:02): Tidak ada alat bantu untuk melakukan sintesa dan kemudian juga membantu penyajian secara efisien, karena juga sekarang lulus pekerjaan itu cepat sekali sehingga ke pendekatan.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (03:14): Dengan model lama yang harus manual entri kemudian tabulasi, itu menjadi tidak visible lagi. Jadi, di kami tuh ada banyak sekali aset digital yang tersebar modeling.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (03:25): Kemudian juga dashboard serta kemudian juga ada portal. Nah, kami itu menghadapi kendala bahwa aset yang tersedia itu belum sepenuhnya terhubung dan kebutuhan untuk melakukan
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (03:48): Tapi dari fragmentasi pengetahuan yang tersebar, lalu kesulitan pencarian entus dokumen, dan belum optimalnya pemanfaatan dokument tersebut, itu menjadi hal yang sering mengemuka. Nah, sehingga memang kami lihat-lihat nih karena.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (04:12): Kami melihat ke dalamnya, ternyata wah cukup menarik. Di situ ada kalau kita masukkan, kami tadi juga apa namanya, malah mencoba juga nih, siapa kepala biro terkoreksi ditiadakan?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (04:24): Oh, dijawab pendek juga berdasarkan semantiknya dan juga referensinya. Nah, terus kemudian ada juga yang apa namanya, tukarannya kan nanyanya udah dari pemilihan apakah keluar. Nah, kok sepertinya?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (04:36): Ini hampir serupa dengan idenya Pak Ses kami, gitu, kita harus mengkonsolidasikan pengetahuan yang ada, aset yang ada, data maupun referensi, dan juga.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (04:48): Dashboard yang ada dari masing-masing unit kerja itu menjadi satu kesatuan, tapi tidak cuma menjadi database konvensional, tetapi mendatabase yang berlandaskan kepada.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (05:00): Ambited EAMbitted. Nah, sehingga memang kami itu kepingin untuk membuat satu yang namanya Makrointelligence Hub. Nah, sebetulnya Makrointelligence Hub kalau versi pemerintah ya sederhana, Pak. Sebenarnya kami
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (05:12): Ada landing page-nya, masuk dulu ke dalam portalnya, di situ ada profil. Tentu saja yang kita lihat di UGM, apa namanya, Digital Center itu kan sudah terpisah.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (05:23): Kita sendiri, Alkalol ini kan memang masih satu portal gitu, ada profil, berita, publikasi, layanan, dashboard public. Itu pada saat nanti ada satu area lagi di situ, kami keinginan untuk punya satu repositori.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (05:35): Knowledge Management Center kami sebutnya perpustakaan PMP. PMP itu Perencana Makro Pembangunan. Nanti di situ kami akan ingin untuk menaruh satu agen.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (05:59): Karena di dalam si perpustakaan PMP itu, sehingga deputi kalau nanti membutuhkan retrieval, itu ya bisa menggunakan izin yang ada di dalam sistem ini untuk mengambil.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (06:23): Wah, ini cocok nih, kita belajar dari UGM. Tentu saja pengalamannya jauh lebih mumpuni, terus kemudian juga apa, secara akademis, literatur, dan lain-lain.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (06:35): Itu lebih bagus dari kami, praktik-praktik terbaik di industri juga pasti teman-teman UGM itu lebih paham, sehingga akses merasa ya, kita datang saja ke sana.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (06:59): Ingin juga punya seperti itu. Apakah setelah unit kerja di kementerian itu sebetulnya bisa nggak sih dibuat? Dan lebih jauh lagi, tentu saja, Pak Karo, nantinya apakah kalau kita melakukan?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (07:11): Policy making proses, apakah pemanfaatannya itu sudah diterima, Pak? Apakah sudah diakui gitu bahwa misalnya policy paper, policy brief seperti itu dengan mem
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (07:23): Manfaatkan instrumen HA yang nantinya dibangun itu apa dalam best practice-nya, teman-teman remisi itu sudah mengakui apakah praktik itu ada di kementerian dan lembaga?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (07:35): Lain atau bahkan di badan atau agensi yang ada di luar negeri, apakah ini sebetulnya sudah menjadi satu praktik yang mulai diterima, Pak? Itu yang kami juga ingin tahu juga, jalan ke depan, ya kan? Kita akan melihat bagaimana pelaksanaannya dan kemudahannya untuk dilakukan oleh masyarakat, terutama dari daerah-daerah.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (07:46): Sampai nanti kita membuat kebijakan berbasis CA, ternyata ini nggak boleh ni secara kaedah akademis tidak boleh, secara ada apa namanya, ada norma-norma dan etika yang harus dipatuhi.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (07:58): Seperti itu yang tentu saja dari akademisi akan lebih memahami dan lebih update dibanding kami yang ada di pemerintahan. Jadi, kira-kiranya konsepnya adalah menempuh satu knowledge management.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (08:10): Repositori dari semua aset-aset digital di unit kerja ke dalam satu portal dedikatif, terus kemudian mengembed di situ agen EA-nya. Agen EA-nya ini tentu saja nantinya.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (08:22): Harus bisa menutup tujuan kami untuk, apa namanya, melakukan penarikan data cepat, kemudian analisis. Nah, sebetulnya ini sudah ada juga ya, Mas Wicky. Ini rencananya kita
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (08:46): Laporan luar negeri itu ya belum tentu masuk ke unitnya. Tanah komputer dapat cengmasukkan direktorat mana? Nah, ini malahan ada teman-teman dari yang membantu saya di tim anggaran ini, Daristan.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (08:58): Terpastaan, tapi karena sekarang AI itu apa namanya, membantu sekali kan? Kita tidak perlu mengetahui bahasa pemrograman, pattern-nya, atau apalah tuh, bisa dilakukan lah?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (09:34): Mana saja? Tapi konsepnya kira-kira pemerintah itu sudah mulai kelewatan, datanya tersebar di mana-mana. Begitu ditanyakan, menterinya ini, "Ah, ini dari baru lagi, bikin lagi dari baru lagi kita."
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (09:46): Regulasi dari baru lagi kan harusnya nggak seperti itu? Harusnya apa yang sudah ada bisa langsung diotomatisin. Kira-kiranya monggo aja Mas Hadif sama teman-temannya, silakan ditunjukkan. Saya mohon izinkan, Pak Karo.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (09:59): Mama masih ada? Merek
**Grady - Sesdep PMP** (10:02): Terima kasih, Bapak Menteri. Ini kami ingin menampilkan apa namanya?
**Grady - Sesdep PMP** (10:14): AI yang kami sudah sebenarnya ini menggunakan AI kan? Sistemnya AIG, jadi ketika kita ada melakukan percakapan dengan AI-nya, nanti AI-nya menjawab.
**Grady - Sesdep PMP** (10:27): Terus hanya menjadi?
**Grady - Sesdep PMP** (10:31): Di dokumen yang kita upload, nah?
**Grady - Sesdep PMP** (10:37): Jadi EA ini kami ke portal, Pak. Jadi di portal ini ada Portal PMP. Nah, ini jadi untuk mengakses AI ini, untuk sementara memang
**Grady - Sesdep PMP** (10:48): Emang?
**Grady - Sesdep PMP** (10:49): Bisa diaksesnya ketika kita login. Nah, login nanti kita masuk ke agent AI-nya pun, ya?
**Grady - Sesdep PMP** (10:56): Nah, di AEA ini ada Playground. Nah, Playground ini di mana kita bisa melakukan tanya jawab yang basisnya adalah dokumen-dokumen yang sudah kita upload dan sudah kita proses, sehingga nanti EA
**Grady - Sesdep PMP** (11:10): Bisa menjawab dengan mudah. Nah, mungkin bisa langsung ditolotkan, kita misalnya ingin mencari apa, misalnya apa sasaran pembangunan di RKP 2017, misalnya, atau de
**Grady - Sesdep PMP** (11:22): Kep dua ribu dua puluh enam?
**Grady - Sesdep PMP** (11:24): Oke aja, silakan.
**Grady - Sesdep PMP** (11:37): Terima kasih.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (11:39): Nanti kafetnya juga dikasih tahu nih ke teman-teman UGM. Jadi ini betul-betul dari pemikiran dasar kami, tidak tahu apa yang terbaik yang tersedia di market gitu, karena biro IT.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (11:52): Kami pusat data dan informasi, kami juga mengembangkan itu sudah cukup, cuma kami melihatnya itu ada terhubung dengan luar, jadi kami takut agak halus sedikit karena kan kalau nggak ketemu sumber dalam, kan dia nyari keluar. Nah, itulah yang kami takuti sehingga tadi Mas Adipati?
**Grady - Sesdep PMP** (12:30): Langsung mencari krisis pembangunan, lalu di saat itu apa namanya?
**Grady - Sesdep PMP** (12:35): Yang dikeluarkan oleh AI itu, itulah rujukan di slide di bawahnya, termasuk dengan timing atau slidenya. Nah, mungkin sederhananya seperti ini untuk yang sekarang?
**Grady - Sesdep PMP** (12:47): Nah, dan ke depannya mungkin nanti kalau di paparan itu, nanti ada kami ingin lebih advance lagi, ada seperti early warning macro system, ya?
**Grady - Sesdep PMP** (12:59): Yang bisnisnya koneai yang ini memang menggunakan API data yang khusus dari BPS, dari OJK, dan kami juga sedang koordinasi dengan Short Economics untuk apa namanya?
**Grady - Sesdep PMP** (13:11): Karena menanyakan mereka punya FPI dan diperbolehkan untuk kita melakukan model konteks protokol, jadi itu nanti bisa membantu kita untuk menghasilkan.
**Grady - Sesdep PMP** (13:22): Kebijakan rancangan kebijakan yang lebih baik?
**Grady - Sesdep PMP** (13:26): Untuk semuanya, untuk selanjutnya di dokumen ini, ada mungkin boleh diklik?
**Grady - Sesdep PMP** (13:33): Di dokumennya?
**Grady - Sesdep PMP** (13:34): Nah, ini daftar dokumen yang sudah kita masukkan. Ini sebetulnya untuk daftar dokumen ini itu kita punya serpihan, jadi kalau teruskan tempe itu dimasukkan dalam
**Grady - Sesdep PMP** (13:46): Serpoin, nah, ini kita akan ke dalam server kita.
**Grady - Sesdep PMP** (13:50): Nah, lalu di dokumen ini juga ada kalian dokument berdasarkan semantiknya, mungkin Mas boleh dibuka sedikit lagi?
**Grady - Sesdep PMP** (14:01): Nah, mungkin di klik semua dokumen, semuah dokumentasi kantor pusat, ah?
**Grady - Sesdep PMP** (14:08): Nah, ini ada relasi dokumen yang kita punya, Pak. Sederhana semantik juga yang ini menjadi database sebenarnya dari RAG yang kita buat di tadi di playground.
**Grady - Sesdep PMP** (14:20): Dan ini mungkin ke depannya juga. Ini belum konek ke dashboard ya, Pak? Dashboard yang tadi ada dashboard kerja, dashboard apa namanya, EWS, Early Warning System. Nah, ini kita mungkin ke depannya kita pengen juga untuk
**Grady - Sesdep PMP** (14:34): Egron itu bisa konek ke dashboard tersebut. Namun egra
**Grady - Sesdep PMP** (14:39): Mungkin itu, Pak Yudus, bahwa yang bisa kami tampilkan untuk sementara ini memang masih cukup sederhana. Nah, untuk platform AI yang kita buat ini, mungkin kami mohon masukannya dari Pak Karo dan.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (14:52): Teman-teman dari Esa, teru gm terkait dengan MPV yang sudah kita buat. Terima kasih, Mas Hadit. Jadi mau izin Pak Karo dan Bapak Ibu dari tim.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (15:03): Makhluk dari UGM, Pak Arif, Pak Farda, Bu Risky, dan rekan-rekannya lain. Jadi, memang kepinginannya adalah lebih efisien saja, Pak, dalam bekerja, lebih efisien, tapi tidak.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (15:15): Menghilangkan ketelitiannya dan apa juga? Dan kemudian juga memberikan nilai tambah karena sekarang itu tersedia banyak sekali platform yang komersial.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (15:27): Arsil gitu, jadi sebetulnya kan kalau secara individu, pribadi-pribadi kan masing-masing berlangganan sendiri-sendirinya, ada ke Mini Pro-nya, ada Cloud-nya, ada Paperflexity, ada dan macam-macam itu, tapi sebagai
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (15:38): Betulnya mungkin nanti Wakarud dan tim juga bisa memberikan arahan kepada kami kira-kira best practice-nya tuh kalau government sector atau untuk yang policy making itu memang yang terbaik tu ini gitu. Terus kemudiannya?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (15:50): Kemudian juga sebetulnya ada, harus ada kehatihan, misalnya, "Oh, ini ada bahayanya juga," dan lain-lain. Itu yang kami tidak tahu waktu hari itu. Yang kami harus belajar dari rekan-rekannya di akademisi, jadi.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (16:02): Secara umum kira-kira visinya seperti itu, Pak, walaupun juga ini yang digunakan kita banyak terhambat juga di dalam birokrasi pemerintah yang saat ini belum terlalu masuk.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (16:26): Langganan pulsa atau Zoom meeting itu sudah teman-teman Dirjen Perbendaharaan sudah paham kalau diajukan bertanggung jawab, tapi Belitoken mereka nanya, "Ini buat apa kamu ni? Kok ngalokasiin sekian?"
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (16:38): Juta apa Klaude atau apaan ini? Nah, itu belum diatur mungkin nih. UGM juga bisa menyuarakan komentar kuat bahwa ini kalau yang sektor government ini ingin lebih advance yang gini-gini harus mulai diatur.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (16:50): Gitu karena ya terus-terang, Pak, kami juga berakrobat sedikit-sedikit gitu karena beli ini nggak bisa, ya, dan nanti dibungkus lah, beli apa gitulah. Tapi kan sebetulnya tidak ideal seperti itu, Pak. Terus kemudian
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (17:02): Ya, apa hal-hal lain yang sebetulnya, kan, dengan Pusdatin, kami sendiri pun sebetulnya, kan, kami seharusnya ini ditempatkan dalam satu server yang sudah katanya level pemerintah, buktinya?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (17:26): Pak, itu nggak beres terdiskusinya. Akhirnya mau nggak mau kita nyari desktop, ya nyari laptop untuk dijadikan ya server kecil-kecilan gitu, Pak, kalau mengandalkan
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (17:38): Kan lokal tes, kan anaknya pulang kantor, mati ya. Mati ya. Ini udah aja kita taruh laptop, nggak colok LAN, tapi kan kayak ngeumpet-umpet gitu nyari report yang terbuka. Akhir teman-teman di
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (17:50): Terus datang saya, dia udah protes, kok ada traffic-nya mau gede banget di.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (17:55): Lantai berapa di unit kerja kami gitu? Nah, hal-hal seperti ini mungkin kami memohon arahan Pak dari teman-teman UGM, sebenarnya secara ininya tuh seperti apa sih, Pak? Selayaknya dalam mengembangkan ini dan mungkin langkah-langkah ke depan apa yang kita
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (18:19): Kira-kira begitu, Pak Karo, rekan-rekan dari UGM, apa namanya maksud dan tujuan kehadiran kami? Kami nanti mohon diberikan penjelasan, Bapak. Kami belajar, mudah-mudahan nanti segera gabung juga di sini.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (18:32): Saya kembalikan ke Pak Karo bila Taufik Welyda. Ya, wassalamualaikum warahmatullah, amin.
**Mardhani - Biro Transdig UGM** (18:39): Baik, terima kasih atas.
**Mardhani - Biro Transdig UGM** (18:44): Intro dan juga paparannya, mungkin izinkan saya untuk merespons sekaligus menyampaikan sedikit apa ya cerita kami bagaimana?
**Mardhani - Biro Transdig UGM** (18:55): Kami memulai dan kemudian sampai per data hari ini, apa saja yang sudah kami bisa hasilkan, tapi mungkin nanti terbagi peran. Saya akan menyampaikan mungkin pada
**Mardhani - Biro Transdig UGM** (19:06): Poin general di mana di situ ada strategi kebijakan dan juga arahnya itu sebenarnya big picture-nya ke mana, gitu ya. Nah, kemudian nanti saya mau dibantu teman-teman juga yang dari tim kami untuk menyampaikan lebih dekat.
**Mardhani - Biro Transdig UGM** (19:19): Terhadap poin-poin yang komponen-komponen yang menurut saya esensial dilakukan. Anyway, saya tadi senang, Pak, dengan saya pernah dua kata kunci yang mirip sebenarnya di kita dengan
**Mardhani - Biro Transdig UGM** (19:43): Kemendes, jadi ya memang menarik.
**Mardhani - Biro Transdig UGM** (19:46): Tapi, Kliwai, mungkin saya sedikit sampaikan. Oke, kita langsung saja nih, Mas Mulyadi. Kami memang salah satu komitmen Universitas Gajahmada untuk mengakselerasi pengembangan teknologi, terutama.
**Mardhani - Biro Transdig UGM** (20:01): Di AI itu adalah kita diberi amanah dari apa namanya setelahnya kami tuh ada Majelis Wali Amanah ini ya? Itu membuat UGM itu menjadi Intelligent University.
**Mardhani - Biro Transdig UGM** (20:13): Jadi nggak cuma universitas biasa, mungkin tadi yang nyebut sekarang lagi muncul kata kunci aneh.
**Mardhani - Biro Transdig UGM** (20:20): University-driven sama juga di government sih, AI-driven Government dan lain sebagainya, tetapi kami menggunakan intelligent university karena.
**Mardhani - Biro Transdig UGM** (20:43): Itu di pengabdian masyarakat?
**Mardhani - Biro Transdig UGM** (20:45): Jadi apa yang kami buat di kampus itu, ya kalau bisa nanti sampaikan atau terasa oleh masyarakat. Dan yang terakhir itu berkait dengan riset, jadi pengembangan, karena kami kompeten. Kami ada di riset. Ya, jadi gitu. Nah.
**Mardhani - Biro Transdig UGM** (21:00): Kami benar-benar menyadari bahwa pernah yang ditemukan pada waktu itu adalah, ya, selalu kalau kita di pemerintahan ini ada regulasinya apa tidak? Ini ada.
**Mardhani - Biro Transdig UGM** (21:11): Ya peraturan main ini apa enggak? Tapi sebenarnya saya tolong jujur, kami memulai dengan regulasi. Berarti jadi di satu setengah tahun lama itu benar-benar kami bekerja liung hukum untuk menyiapkan itu semua peraturan.
**Mardhani - Biro Transdig UGM** (21:26): Yang ter yang kami punya ini itu sebetulnya di tahun akhir tahun kedua bahkan, nah memang ini menunjukkan bahwa untuk bisa kita mengejar regulasi di awal itu kita akan kehabisan waktu. Nah, sehingga padahal dari sisi teknologi.
**Mardhani - Biro Transdig UGM** (21:42): Oki, dari sisi challenge itu kan kencang sekali ya, jadi kita pun ketinggalan, sehingga waktu itu saya meminta izin kepada pimpinan, yaitu, "Izinkan kami melakukan kesalahan dalam melakukan inovasi ini."
**Mardhani - Biro Transdig UGM** (21:54): Walaupun ada kesalahan ya?
**Mardhani - Biro Transdig UGM** (21:56): Maksud kami, ya, lebih baik kami minta maaf daripada minta izin, kan kira-kira begitu. Jadi, cara Bapak Ibu melakukan dengan cara mencolok sembunyi-sembunyinya itu adalah the best practice menurut saya, bukan kesalahan. Jadi sama cahaya.
**Mardhani - Biro Transdig UGM** (22:25): Gini, misalnya, sehingga efeknya, kami harus punya ini, nyebutnya saya sebut playground kalau kami sentak deh, jadi gitu. Sebenarnya yang mengusulkan jangan senpot ya, tapi anwaja apa namanya sens?
**Mardhani - Biro Transdig UGM** (22:36): Kediri ini memang benar-benar untuk dipukul-pukul dulu, jadi semacam itu. Jadi, agar kemudian untuk dicoba. Untuk terakhir, kita punya Inovasi dan seterusnya dari macam-macam itu. Mungkin next, Mas Alif?
**Mardhani - Biro Transdig UGM** (22:48): Ah!
**Mardhani - Biro Transdig UGM** (22:50): Kami tadi ke.
**Mardhani - Biro Transdig UGM** (22:51): Regulasi itu juga karena kami di pilot transformasi digital. Kami punya segini. Nah, saya ini begini, Bapak, Ibu. Nah, mungkin menjawab tadi Bapak, Ibu terkait dengan saylo. TADI sebenarnya begini, kita sudah ada kebutuhan untuk melakukan menbius.
**Mardhani - Biro Transdig UGM** (23:06): Data dalam dashboard dan tempat-tempat manfaatkannya dengan AI?
**Mardhani - Biro Transdig UGM** (23:10): Jebakan pertama ya melalui bahasa kami itu adalah kita terdesak-desak ke situ, bang. Seriously, jadi efeknya ceritanya error terus langsung bikin dashboard tampil, tapi kok nggak ada efeknya? Enggak impor?
**Mardhani - Biro Transdig UGM** (23:24): Ya bikin AI tools macam ini?
**Mardhani - Biro Transdig UGM** (23:27): Ya, cuma gini, kira-kira begitu. Nah, cuman terus ini nyadari di satu tahun pertama kami menemukan flunya bahwa ternyata permasalahannya bukan di datanya atau sistem yang existing, tapi proses bisnis lah.
**Mardhani - Biro Transdig UGM** (23:41): Nah, jadi begini, kalau di AI itu kan ada istilah gear pitch-in, gear pitch-out. Pengen kita masukkan nanti akan ditertutasi AI seperti itu. Nah, kedal informasi yang kita masukan ini, ini kan diproses dalam kegiatan musyawarah dan perencanaan nasional (MusRenBang).
**Mardhani - Biro Transdig UGM** (23:53): Sebuah aktivitas, ya. Nah, kadang kita mikirnya yang penting punya data, tapi kita tidak berpikir bahwa sebenarnya datanya harus high quality, harus baik. Nah, untuk memperbaiki ini.
**Mardhani - Biro Transdig UGM** (24:04): Prosesnya harus dibenerin.
**Mardhani - Biro Transdig UGM** (24:07): Nah, ternyata problem karena kita kan integrasi itu, Pak, kena silo itu atau tidak terintegrasinya kita? Karena memang kita punya proses bisnis masing-masing.
**Mardhani - Biro Transdig UGM** (24:15): Ganti terus nih bicara pun yang laku, misalnya, "Oh, ini sama," "Oh, ini beda," dan lain sebagainya. Nah, ini pertama adalah next, Mas Tali, adalah kami mencoba membenar
**Mardhani - Biro Transdig UGM** (24:28): Kahinya dengan membuat sebuah konsep dan impres arsitektur kan?
**Mardhani - Biro Transdig UGM** (24:34): Nah, apa tuh yang terkait tur? Ini adalah kita ulang buat, jadi saya bilang menata ulang, bahkan mungkin karena seorang komputer sains, ya, ini bukan menata ulang, Mbak, tapi rekonfigurasi ulang semuanya, gitu loh kalian kalau orang.
**Mardhani - Biro Transdig UGM** (24:46): Dengan dari pagang benerin kan mending bikinin perubahan gitu jadi semacam itu. Jadi sama seperti begitu, tapi yang kami lakukan adalah.
**Mardhani - Biro Transdig UGM** (24:54): Uang pertama, kami memotret benar, Pak, proses bisnis dari orang mengatur pikir ketika masuk ke UGM sampai dia lulus mahasiswa terlurus. Kami potretnya, jadi kami memberikan sebenarnya mungkin.
**Mardhani - Biro Transdig UGM** (25:22): 10 motor itu bukan berarti hanya seratus motornya, tapi ada proses satu kali orang memastikan mobil dan seterusnya. Itu lagi tuh dipakai untuk tiap proses, Bpk. Ibu. Nah, dengan cara ini.
**Mardhani - Biro Transdig UGM** (25:34): Kita jadi belum, Bapak, Ibu, bahwa ketika kita nanti mau menggunakan data itu, benar-benar kalau berdasarkan saya tuh di end datanya itu, nah kira-kira gitulah. Sering nggak pakai, Bu?
**Mardhani - Biro Transdig UGM** (25:45): Dapat laporan kayak tadi, dikumpulkan dokumennya, nanti protesinya jadi tadi yang disampaikan tadi sambil tipunya Bapak bisa ditanya? Bisakah sampainya begitu, gimana rumusnya?
**Mardhani - Biro Transdig UGM** (25:57): Apa semua?
**Mardhani - Biro Transdig UGM** (25:58): Langkah pertama di algoritmanya nih keran teknis yang durat. Langkah kedua, kita nggak pernah kesul datanya bagaimana data itu muncul menjadi masalah. Nah, ini ya?
**Mardhani - Biro Transdig UGM** (26:21): Ikut jalan membangun dashboard dan ini investasi nih kalau kata saya ni. Kalau orang teknis sebenarnya ini yang harus dilakukan, Mbak. Harus ada orang yang mau tuh cipleng, Mbak, beresin proses bisnis.
**Mardhani - Biro Transdig UGM** (26:33): Nah gitu. Nah, kalau ditanya tugasnya siapa, mungkin ada Biro Perencanaan ji, Pak. Misalnya Biro Perencanaan Organisasi harus jawab pertanyakan di situ, Pak. Tapi kalau tidak bisa ya?
**Mardhani - Biro Transdig UGM** (26:45): Seperti kami karena di unit khusus namanya Biro Transformasi Digital ini, kami harus melakukan itu. Memang tiap awal saya juga lupa, pusing sekali tuh. Nah, ini gimana ceritain ya, jadi tugas-tugas tapi nyuci.
**Mardhani - Biro Transdig UGM** (26:57): Ding, banyak orang nih kira-kiranya, tapi saatnya melakukan, Mbak, karena ini investasi tidak hanya sekarang, tetapi pan efeknya, Mas. Sekarang kita punya semua proses bisnis di setiap di mana?
**Mardhani - Biro Transdig UGM** (27:21): Kita udah fokus ke tupai, Mbak, dengan cara ini, Mak?
**Mardhani - Biro Transdig UGM** (27:24): Saya bisa mendesain, mentransformasi depan itu, cara kita parkir motor itu tidak lagi parkir visual. Nah, kira-kira begitu. Nah, ini evaluasinya buat tuh, jadi kita total sudah.
**Mardhani - Biro Transdig UGM** (27:39): Jalan hampir penuh nih. Kalau tahun ini berakhir yang per tahun gitu, kita membangun itu. Nah, ini menarik beberapa buat soalnya masalah mungkin kita bisa lihat kan data jumlahnya dia?
**Mardhani - Biro Transdig UGM** (28:08): Kemudian aplikasi dan juga teknologi, Bapak, Ibu. Nah, ini jadi Bapak, Ibu bisa bayangkan kita di level ini, di level universitas, mas, itu 3.985.
**Mardhani - Biro Transdig UGM** (28:20): Prosedur proses bisnis atau mungkin dokumen SOP lah, apa itu jadi?
**Mardhani - Biro Transdig UGM** (28:26): Ya, ini kalau saya suruh menyerengin gitu ya, stres sih, Pak. Jadi, dia harus pakai i juga untuk melakukan itu, tapi kita lakukan, Pak, baru saja merevisi.
**Mardhani - Biro Transdig UGM** (28:38): Nah, nanti hasilnya adalah kita bisa punya ini proses bisnis. Jadi, anggaran split tadi yang mau dibuat itu nggak cuma orientasinya tuh menampilkan.
**Mardhani - Biro Transdig UGM** (28:58): Nun, saya pun jadi mohon maaf sekali, ya, saya bilang ini kalau dashboard-nya itu hanya digunakan untuk mengambilkan data-data yang membuat pimpinan seneng, menurut saya tuh bukan insight.
**Mardhani - Biro Transdig UGM** (29:09): Tapi kalau pembentukan pimpinan itu dengan meja, itu keberhasilan dashboard benar-benar gitulah. Tidak ada yang terus-meneruskan.
**Mardhani - Biro Transdig UGM** (29:19): Nah, lalu dengan.
**Mardhani - Biro Transdig UGM** (29:21): Nggak ketika dengan Bu Riktar itu tiga-tiga deh gitu, sebanyak satu sesis selama ini kan seperti nih. Berikutnya, selama ini kan bagus-bagus ya angkanya. Ya, semua senang dengar, lihat tu.
**Mardhani - Biro Transdig UGM** (29:31): Saya sampaikan yang jelek-jelek, Jitu, bahwa itu baru mengubah. Ternyata memang efektif di sini, jadi tahu apa yang harus diperbaiki, kembangkan. Tapi Bapak-Nenek tua tuh data Indonesia, ya. Jadi mungkin selama ini teman-mu
**Mardhani - Biro Transdig UGM** (29:43): Nggak usah nyambut politik, kira-kira begitu. Next, jadi ya ini satu, mungkin nanti detailnya Mas Elir. Kemudian yang kedua, Bapak Ibu, mungkin saya agak sedikit lompat sih yang
**Mardhani - Biro Transdig UGM** (29:55): Lalu strategi kedua, Bapak, Ibu, adalah kita fokus ke.
**Mardhani - Biro Transdig UGM** (30:01): Satu pertanyaan mendasar untuk kita membangun tadi, yang itu bagus banget, Pak. Menurut saya, itu harus dilakukan dan saya mendorong ada organisasi di pemerintahnya harus mulai, yaitu kita har
**Mardhani - Biro Transdig UGM** (30:13): Menghadirkan dulu kita punya data itu, ternyata baik, Bu, tapi kemudian tidak tahu bahwa?
**Mardhani - Biro Transdig UGM** (30:21): Datanya bisa digunakan untuk itu cukup sulit. Nah, ini kami punya peta, ya, Bu. Datanya UGM itu kami petakan dulu, tapi data-data yang bisa kita konsumsi, apa yang bisa kita gunakan?
**Mardhani - Biro Transdig UGM** (30:33): Saya paham karena timeline kita pun data yang inginkan idealnya bisa dipastukan dasar privacy boleh dibukti publis ya sudah kami kayak sebagai orang Jawa lah sekitarnya lipir-lipiran aja carik datanya.
**Mardhani - Biro Transdig UGM** (30:48): Data yang benar-benar otom? Iya, kan kadang-kadang saya naik itu. Saya hadirkan adalah data yang sebenarnya dari luar. Yang otomatis bedanya dengan yang di dalam. Untanchengyang bener. Oh, iya, jadi.
**Mardhani - Biro Transdig UGM** (31:00): Ibu pernah ngake yang kanunya ya? Tapi ini datanya kita kira-kirain, datanya di sana semua, enggak bohong lah. Pancingnya juga gitu-gitu, tes nanti cinta.
**Mardhani - Biro Transdig UGM** (31:12): Inilah baru data yang ngalir, kadang begitu. Jadi kira-kira begini, memang harus ada strategi seperti itu ya, tapi intinya mereka harus punya petanya dulu di awal.
**Mardhani - Biro Transdig UGM** (31:21): Data ini punya yang biru mana? Data ini punya di petikan mana itu dulu, Pak, karena itu nanti jadi seragam langsung Bappenas akan Bappenas bisa lihat tuh beberapa kumpulan data yang menjadi satu, sorry, misalnya yang kuning gitu lah. Jadi punya
**Mardhani - Biro Transdig UGM** (31:36): Kalau dahulu BMCT atau Menko itu dimensinya itu adalah terkait dengan pendidikan dan pengajaran, lansterusnya jadi ini titik cap-nya secara universal dapat, nah kita.
**Mardhani - Biro Transdig UGM** (31:48): Perlu strategi itu, Pak. Saya nggak tahu ini, mungkin dari debutnya Pak Yunus lebih fokus atau mana bisa mengancing ke depan yang lain untuk melihat ya, karena kena konsteksi?
**Mardhani - Biro Transdig UGM** (32:00): Kemenperin? Mungkin overview-nya memang benar-benar Indonesia banget ya, Pak. Jadi semacam itu. Nah, ini yang benar dari kan multidimensi dan lain sebagainya. Next to next. Nah, kembali ke UKM saja, naik pusat.
**Mardhani - Biro Transdig UGM** (32:12): Kami setelah itu, kami akan punya bentuknya apa?
**Mardhani - Biro Transdig UGM** (32:16): Nah, kami punting Bapak, Ibu, yaitu dengan menggunakan UGM semacam set mesin sederhana awalnya untuk mendisplaykan kita punya data apa?
**Mardhani - Biro Transdig UGM** (32:28): Nah, Pak Pepu bisa cek di SBS UPMACID, sekarang sudah berevolusi dari ini ya? Ini itu kita.
**Mardhani - Biro Transdig UGM** (32:36): Membuat sebenarnya ini apa pesaingnya? Kita punyai data yang umum secara publik dan yang publik itu ya satu kritis dari penggunaan data itu karena enivdata itu publik gitu kan, bukan datanya internal yang
**Mardhani - Biro Transdig UGM** (32:51): duh lah!
**Mardhani - Biro Transdig UGM** (32:52): Nah, tak, itu jadi kita sama-sama punya cross check, mana versi yang paling benar? Misalnya nih, Bapak Epo, saya kumpulkan data, tapi data rektor bertahun-tahun lah ini.
**Mardhani - Biro Transdig UGM** (33:01): Itu ada, nah, tapi sebenarnya dengan cara ini, satu, kita mengintegrasikan data menjadi satu tempat. Yang biasanya itu di masing-masing Bappenas sudah berapa website tuh, Pak? Iyo.
**Mardhani - Biro Transdig UGM** (33:12): Unit kerjanya pasti punya sendiri kan, nanti dijadiin ngapa, biarin, tapi data yang publik itu ke platform. Kemudian kita punya orang, mudahnya gini, bahasa usernya ya, orang nyari tuh satu tempat aja gitu, nah.
**Mardhani - Biro Transdig UGM** (33:27): Kira-kira sebenarnya ending-nya gitu, tapi strategi di belakangnya bagi orang AI itu strategi ngumpulin data?
**Mardhani - Biro Transdig UGM** (33:33): Kan gitu, eksploitasi terus keren seperti yang Bapak tadi temukan, tapi ketika nggak punya datanya, ya lewat juga. Kami coba pengalaman buruk, Pak. Jadikan berarti ini pengamatan sih jika nanti tertutup dari
**Mardhani - Biro Transdig UGM** (33:48): Informasinya itu kita kumpulkan dulu dan ternyata informasi yang di luar itu lebih dominan, jadinya artikel bilang yang salah, misal gitu, mungkin kan? Informasi yang salah. Jadi negara begitu, nah, itu bisa ke
**Mardhani - Biro Transdig UGM** (34:00): Jadi juga nah?
**Mardhani - Biro Transdig UGM** (34:02): Selamat datang, Pak Sesi. Selamat datang. Maaf sih, sudah maaf nih, Pak Sesi. Ini ada mata dornya ya? Ada matanya?
**Mardhani - Biro Transdig UGM** (34:18): Soalnya lagi jadi kita lanjut. Jadi di situ itu kemudian terus sebenarnya ini Kemudiasi kedua kami jadi EA.
**Mardhani - Biro Transdig UGM** (34:30): Luar biasa cepat proses bisnis datanya existing, baru di situ kita bisa bangun AI-nya. Ti yang Bapak Ipucah, AIs kami bisa mengenerate informasi dan seterusnya.
**Mardhani - Biro Transdig UGM** (34:41): Itu ya sebenarnya di-support oleh data itu.
**Mardhani - Biro Transdig UGM** (34:45): Jadi kita gitu. Nah, ini yang menarik, kemudian bisa macam-macam, ternyata bisa dikembangkan untuk kalau punya layanan untuk bahasa Inggris. Kemudian untuk sekarang untuk macam-macam.
**Mardhani - Biro Transdig UGM** (34:57): Dan seterusnya, jadi itu bisa dilakukan. Satu sisi, secara pelayanan ke mahasiswa menjadi lebih simple. Nah, yang mungkin terakhir dari saya adalah tidak berhenti di situ, Pak, karena kami punya kewajiban.
**Mardhani - Biro Transdig UGM** (35:24): Sama sel satu.
**Mardhani - Biro Transdig UGM** (35:26): Satu semester ini dengan kondisi, Pak?
**Mardhani - Biro Transdig UGM** (35:30): Jadi ini yang bapak-bapakan, bukan diagram ya, mungkin mirip dengan yang sudah pernah saya sampaikan. Sebenarnya kami punya namanya Intelijen Daspo. Ini sama dengan Komisi Komdis, kemudian memberikan use case-nya. Kami yang mengerjakan in
**Mardhani - Biro Transdig UGM** (35:44): Ini mengambil data dari beberapa, bahkan banyak sosial media dan sumber/media nasional di crawling. Nah, ini disibaratkan nanti crawling-nya sumber yang tadi, data-data Bapak tadi, nah dari situ.
**Mardhani - Biro Transdig UGM** (35:59): Kita juga AI dengan sentimen analisis macam-macam begitu, yang ujungnya itu tidak hanya menghasilkan satu berita, itu tidak nyata, tapi isu.
**Mardhani - Biro Transdig UGM** (36:12): Misalnya sekarang tentang apa ya? Sekarang karhutla mungkin gitu ya, itu muncul begitu misalnya, atau yang lain. Nah, ketika itu sudah bisa dihasilkan seperti ini, mesin akhirnya bisa memprediksi.
**Mardhani - Biro Transdig UGM** (36:35): Informasi ke bapaknya bahwa tadi kalau pertanyaan terakhir Bapak tadi terkait dengan regulasi AI di Indonesia?
**Mardhani - Biro Transdig UGM** (36:42): Kita dengan komisi sudah melangkah jauh seperti ini. Jadi, menurut saya sudah tidak ada isu terkait dengan pemampatan AI untuk di pemerintahan.
**Mardhani - Biro Transdig UGM** (36:53): Ini kemarin kita dapat informasi juga, ini sudah dipakai sama Bu Menteri, dapet gilbap diubah jadi oke. Jadi macam itu, nah. Ini yang menarik gitu. Nah, ini simpokis dan
**Mardhani - Biro Transdig UGM** (37:05): Dan nggak simpel sih, tapi pekerjaan cukup panjang juga, dan ini bisa menjadi kita replikasi karena misalnya nanti berkenaan untuk kerja sama dengan kami dengan modal seperti AITF itu, saya pikir sangat-sangat bagus.
**Mardhani - Biro Transdig UGM** (37:17): Juga gitu ya, jadi itu bisa dikembangkan bersama-sama. Nah, mungkin itulah overview-nya, Pak. Mungkin saya serahkan Mas Alif sedikit untuk memberikan lebih detail, mungkin tidak keluar lama-lama, ya nanti.
**Alif - Biro Transdig UGM** (37:29): Biar bisa banyak, terus bisa diskusi ya. Terima kasih, Pak Mardhani. Nah, mungkin tadi menyambung sedikit soal review yang disampaikan Pak Madani, memang
**Alif - Biro Transdig UGM** (37:53): Kualifikasi atau di beberapa buku menyebutkan itu dari lama gitu ya, terjadi tsunami data ketika datanya tidak bisa diolah. Jadi, ada kita punya data tapi kita tidak tahu ini darahnya bisakah?
**Alif - Biro Transdig UGM** (38:05): Ya, apakah yang kita, ya, memang tadi kami mulainya dari bahasa arsitektur, mungkin kalau saya tunjukkan lagi tadi secara detail sedikit, sorry?
**Alif - Biro Transdig UGM** (38:17): Nah, kalau di sini sebenarnya mungkin tadi sebutannya baru proses bisnis saja, tapi sebenarnya di dalam sini isinya termasuk data dan regulasi serta.
**Alif - Biro Transdig UGM** (38:28): Visi misi atau KBI apa yang mau dicapai? Mungkin saya tunjukkan sedikit, mungkin kalau di Bappenas atau di Kemenrian sebutannya dulu SDG's.
**Alif - Biro Transdig UGM** (38:40): PBE mungkin sekarang pemerintah digital yang masih minta data dari Pan-RB gitu ya?
**Alif - Biro Transdig UGM** (38:53): Nah, ini bekal kami memang awalnya dari sini, gitu. Memang prosesnya sangat panjang. Ini sebenarnya proyek yang tidak ada garis finish-nya, gitulah. Jadi, saya mencoba mengejar.
**Alif - Biro Transdig UGM** (39:03): Seratus persen atau kami tapi nggak bisa gitu, rata-rata di 99,5 gitu. Karena apa? Karena layanan dan proses itu yang ada di UPM pun berkembang terus setiap bulannya ataupun tiap tahunnya gitu, hampir sejak
**Alif - Biro Transdig UGM** (39:15): Tiap bulan kami menerima request sistem atau layanan baru, jadi kami perlu memetakan juga apakah sistem yang direquest ini sebenarnya sudah ada ataupun sedang dikembangkan?
**Alif - Biro Transdig UGM** (39:27): Karena jadi kita tidak perlu mengebarkan sistem baru ini, contohnya respon yang paling proses bisnis yang paling detail di kami. Jadi, kami mengkoneksikan seluruhnya mulai dari IAO atau rencana strategis.
**Alif - Biro Transdig UGM** (39:39): Universitas, kemudian regulasi di bawahnya ada layanan ini yang terbaru karena kami juga mematok dari Bappenas atau pemerintah digital karena kami dibawanya Kemenkominfo.
**Alif - Biro Transdig UGM** (39:50): Di slide kuartal itu di bawahnya cukup gede, jadi seluruh aplikasi kemudian data, proses bisnis, alurnya seperti apa dari start sampai end-nya. Kemudian aktor-aktornya atau pelaksananya juga kelihatan. Jadi kalau di sini kita klik misalkan
**Alif - Biro Transdig UGM** (40:05): Saya mau jadi rektor gitu ya?
**Alif - Biro Transdig UGM** (40:08): Misalkan jadi saya sudah tahu data apa yang atau proses apalah yang mau saya rawal ke depannya dan di situ saya harus ngapain, itu akan terlihat kan. Kemudian di bawah juga kami tidak
**Alif - Biro Transdig UGM** (40:20): Yaitu, tapi kami tambahkan 2, Pak, risiko dan TJK atau GBI. Jadi, oh, di proses ini ada risiko apa saja yang mungkin muncul, data-datanya mungkin tidak terdeteksi, dan lain-lain. Dan GPI-nya apa, gitu ya? Itu mungkin.
**Alif - Biro Transdig UGM** (40:35): Sedikit penjelasan tantangan terkorespondenator untuk menjadi bahan kami perkembangan AI gitu, itu kemudian mungkin ini sedikit beberapa link yang bisa diakses.
**Alif - Biro Transdig UGM** (40:46): Di sini, Bapak, Ibu, jadi nanti boleh di-versani atau dilihat, kalian ada beberapa untuk website utama kami ada di aiugmas.id, khusus untuk AI, kemudian port disaster ini dengan Pak Farda yang
**Alif - Biro Transdig UGM** (41:01): Untuk pemetaan bencana, kemudian ada Semata Agrini untuk AI di
**Alif - Biro Transdig UGM** (41:06): Tanyaan kita bertanyaan dan berobunan sudah bekerja sama juga dengan beberapa industri ini dari ATP, kemudian kami juga ada namanya, nah ini tadi seperti yang di Bappenas lakukan, jadi kami juga punya lab tersendiri, Pak, untuk mengembangkan.
**Alif - Biro Transdig UGM** (41:22): Inisiatif-inisiatif kami yang memang tidak bisa diwadahi langsung dengan DTI, jadi kami punya apa ya, server kecil gitu untuk meniling semuanya, kemudian EA-nya tadi ini untuk yang sesuai dari Kampar.
**Alif - Biro Transdig UGM** (41:34): Kan yang terakhir ini analitik sebenarnya di sama didedeslabwebid ya, jadi isinya di sana kumpulan seluruh riset Gabina. Ini kalau ingin lihat, mungkin saya tampilkan sedikit gitu, ya?
**Alif - Biro Transdig UGM** (41:59): Nah, ini di beberapa katalog kami, jadi mulai sebenarnya ada Pak Titi nih. Kalau hari Minggu, Pak Tidi Monggok dicekal, saya lanjutkan kepada dia, limastarnya?
**Alif - Biro Transdig UGM** (42:09): Yang punya sektornya ini?
**Dedi Eko - Biro Transdig UGM** (42:12): Ya betul, Nuan, selamat pagi. Betulan, Mas Halip, Pak Madari, Manajin. Jadi saya, nama saya Tedi Eko. Saya posisi ada tukang obrek di PTD. Tujuan saya adalah menjadi engineer tukang yang
**Dedi Eko - Biro Transdig UGM** (42:39): Bahwa kalau Mas, mudah-mudahan berbasis WordPress yang menampilkan semua inisiatif yang dilakukan kami, tim kecil yang ada di PTD. Saya sebetulnya karena esponya Tim BTD hanya saya, pimpinan.
**Dedi Eko - Biro Transdig UGM** (42:51): Yang di depan dan Mas Alib, ya sebenarnya yang itu saja. Ini adalah cara kami mencoba memotret semua upaya usaha dari Pak Maden menyebut.
**Dedi Eko - Biro Transdig UGM** (43:27): Kemudian sudah bisa langsung menangkap apa yang ada di sini ya. Kita tadi era-era ini juga pakai DB pasti atau pakai vektor DP juga pastinya, kemudian jadilah masuk ke bawah, Mas Alif, iya?
**Dedi Eko - Biro Transdig UGM** (43:39): Yang apa yang beberapa kami deposkan ada hubungan dengan EA atau ada juga kemudian CCTV Google itu menunjukkan kami itu di New York.
**Dedi Eko - Biro Transdig UGM** (43:51): Berusaha untuk mengadopsi yang sudah jadi.
**Dedi Eko - Biro Transdig UGM** (43:55): Karena fransip itu kan kita harus pikir sendiri ya?
**Dedi Eko - Biro Transdig UGM** (43:58): Itu untuk kami adalah cara kami mengelola situasi yang sudah jadi kita deploy, itu juga udah berapa pun juga. Nah, ternyata di dì
**Dedi Eko - Biro Transdig UGM** (44:08): I kami melangkah itu tuh sesuatu yang jadi aneh di bawah masuk dicoba produksi itu dia belum ada tempatnya, nah sehingga kami memposisikan di meeting ini selain.
**Dedi Eko - Biro Transdig UGM** (44:20): Perangsang dari jadi ada konsep proses bisnis supaya apa kita sinerginya?
**Dedi Eko - Biro Transdig UGM** (44:40): Contohnya ini jadi.
**Dedi Eko - Biro Transdig UGM** (44:42): Ya, ini adalah contoh sistem menterian yang dibuat oleh menggunakan AI untuk menyelesaikan kebutuhan di unit.
**Dedi Eko - Biro Transdig UGM** (44:50): Jadi sudah lancar jalan. Jadi saya, kami sebagai engine man.
**Dedi Eko - Biro Transdig UGM** (44:55): Dengan posisi sebagai pengembang, kemudian mengembangkan sebuah sistem jalan dipakai oleh internal?
**Dedi Eko - Biro Transdig UGM** (45:03): Kemudian kalau program diakusi di situ justru kan ke mana-mana masih defl seperti itu. Jadi kita punya pelajaran. Jadi platongan yang disebutkan di Bappenas tadi, kalau dikami di PTD?
**Dedi Eko - Biro Transdig UGM** (45:16): Tempatnya adalah seperti ini. Nah, kemudian yang berarti artinya sebenarnya apa? Pelaksanaan.
**Dedi Eko - Biro Transdig UGM** (45:23): Bukan prosesnya, teman-teman, kalau saya kasih tahu apa yang Bapak/Ibu lihat, itu tidak ada manusia mengerjakan. Percaya atau tidak?
**Dedi Eko - Biro Transdig UGM** (45:33): Ya mispa?
**Dedi Eko - Biro Transdig UGM** (45:35): Ini kemudian manfaat seperti kemasalib ya, sistem artificial kita semua menggunakan AI, tidak perlu manusia. Memang bagaimana itu, saya nggak paham tanpa programmer sih?
**Dedi Eko - Biro Transdig UGM** (45:49): Memang AI itu sekarang membantu memangkas.
**Dedi Eko - Biro Transdig UGM** (45:52): Nikel tadi banyak sekali, jadi kita bisa tiba-tiba seorang akuntan bisa bikin dasar sendiri. Tiba-tiba seorang natura usaha bisa bikin sebuah desktop sendiri. Pencari presentasi natura, bahkam i, yaitu Samwawadai I.
**Dedi Eko - Biro Transdig UGM** (46:07): Itu supaya minimal ada satu wadahnya, ya. Ini inisiatif kami. Nah, jadi katanya kalau saya boleh mengarang, minimal engineer yang dari Bappenas siapa?
**Dedi Eko - Biro Transdig UGM** (46:19): Minimal bisa membuat satu wadah. Wadah itu sudah dikomunikasikan, gimana caranya supaya bisa dilihat, misalkan ke internal atau apa, untuk mempercepat prosesnya?
**Dedi Eko - Biro Transdig UGM** (46:30): Oke, nah, di belakang ini semua kami juga mengenalkan sebuah konsep yang namanya agentik AI. Apakah di Pertunas sudah mulai bergerak?
**Dedi Eko - Biro Transdig UGM** (46:40): Sepertinya sampean gini, nah?
**Dedi Eko - Biro Transdig UGM** (46:42): Ini semua dikerjakan oleh agenda AI dan platform yang kami gunakan adalah Hermes. Itu ada Hermes, Mas, ya?
**Dedi Eko - Biro Transdig UGM** (46:49): Nah, itu di situ. Jadi tadi Sugeng sama dengan atau Gila Merutap itu ada?
**Dedi Eko - Biro Transdig UGM** (46:58): eh?
**Dedi Eko - Biro Transdig UGM** (46:59): Saya sekalian saya sebutkan, Mas, jadi UGM Router itu adalah LLM yang kami gunakan untuk.
**Dedi Eko - Biro Transdig UGM** (47:07): Kami membagikan.
**Dedi Eko - Biro Transdig UGM** (47:10): Tapi Pak Menteri cukup baik hati, mengadakan, memberikan tamu, kemudian berikan teman-teman yang mau mencoba tema-tema ini.
**Dedi Eko - Biro Transdig UGM** (47:20): Gitu nih, kami langganan apa kalau lewat telepon ya? Kami langganan Open Air, Letafomia, Depsik juga, jadi kami kasih.
**Dedi Eko - Biro Transdig UGM** (47:32): hm。
**Dedi Eko - Biro Transdig UGM** (47:33): Ayo, kami mau coba. Boleh, ayo. Jadi kalau langsung kita buka activity.com, sudah buka cloud-nya. Sekarang kita, ayo, manfaatkan model-nya, bukan intraveisual?
**Dedi Eko - Biro Transdig UGM** (47:47): Webnya, nah, tapi yang paling bangun adalah model ditambah dengan kin, jadi pelatihan mereka menggunakan adalah Hermes. Mungkin sudah pernah dengar Hermes sih, ya, salah sekaligus?
**Dedi Eko - Biro Transdig UGM** (47:59): Kata saya sebutkan, jadi yang sedang kami riset adalah caranya, caraannya Hermes yang ada di yang itu open, ya. Itu bisa diajukan kemudian disesuaikan dengan pola kerja sama yang ada di BPDM.
**Dedi Eko - Biro Transdig UGM** (48:11): Mau dikembalikan ke yang halaman tadi, Mas? Yang ada Hermesnya, Mas Salik.
**Dedi Eko - Biro Transdig UGM** (48:17): ya.
**Dedi Eko - Biro Transdig UGM** (48:18): Kertasnya ada beberapa, kayak ya?
**Dedi Eko - Biro Transdig UGM** (48:22): Ya.
**Dedi Eko - Biro Transdig UGM** (48:24): Ya itu ya izin rantam itu dibuat aja, buka saja gitu, nah?
**Dedi Eko - Biro Transdig UGM** (48:29): Ya learn more, yeah?
**Dedi Eko - Biro Transdig UGM** (48:32): Nah, jadi ini sedang saya uji coba di Hermes. Itu yang sekilo adalah sebuah platform terbuka untuk agent AI, namun di situ sangat mudah belajar. Nanti dibukakan lagi bisa tiga pasca.
**Dedi Eko - Biro Transdig UGM** (48:59): Analit visa mau jadi asisten mengelola Visa?
**Dedi Eko - Biro Transdig UGM** (49:02): Karena dia kan belum, saya mengingat Anda. Nah, itu yang akan kami turunkan aslinya. Jadi, kita bikin beberapa agentik yang memang spesifik, misalkan agen visual di mana menganalisis CCTV membantu kalimat.
**Dedi Eko - Biro Transdig UGM** (49:17): Baik, waktu kita meeting ini?
**Dedi Eko - Biro Transdig UGM** (49:18): Mainnya sih.
**Dedi Eko - Biro Transdig UGM** (49:20): Mewah anomali, misalnya, kan?
**Dedi Eko - Biro Transdig UGM** (49:23): Ada orang yang people counting delapan malam, ya rasanya sudah tidak ada orang meling. Ya sebenarnya OGM agent untuk visual bisa hal lain di person?
**Dedi Eko - Biro Transdig UGM** (49:35): Kami ada dokumen-dokumen untuk banyak fisik scan-scan itu yang harus dikonversikan secara manual. Saat ini sudah dikonversikan dari dokumen di-scan jadi gambar.
**Dedi Eko - Biro Transdig UGM** (49:47): What's next? Ada yang namanya UGM Agendik Vision. Dia mengkompilasi semua dokumen, diambil OCR-kan, dia masukkan ke KIPRN supaya
**Dedi Eko - Biro Transdig UGM** (49:58): Diusahakan datanya oleh RAK. Itu bukan saya, Jentik. Jadi, Jentik tuh memang mengejakan barang yang kecil-kecil. Kayaknya next dari evaluasi yang teman-teman lakukan di Bappenas adalah mengembangkan.
**Dedi Eko - Biro Transdig UGM** (50:10): Agen yang bisa mengkonversi dokumen tadi di belakang itu bagus sekali kalau MBCM luar biasa sekali, tapi kita sudah bisa bantu dulu dicegah scan semuanya, nanti agen TI bisa ngambil.
**Dedi Eko - Biro Transdig UGM** (50:22): itu?
**Dedi Eko - Biro Transdig UGM** (50:23): ke sebuah hal bisa dikonversi, masukkan ke DB, terus dilakukan secara otomatis.
**Dedi Eko - Biro Transdig UGM** (50:55): Menarik proses yang ada di dalam si istimewanya sekretari dan itu ternyata terjadi, ya itu karena memang dia menanyakan sesuatu yang saat itu belum ada single source of truth-nya, jadi.
**Dedi Eko - Biro Transdig UGM** (51:25): Tadi sudah bicara agen tik AI kami, sekarang arah itu. Jadi, kalau rekan-rekannya melihat ini, kayaknya selain tuh ya terusik dengan router tadi, juga dengan memilih platform untuk.
**Dedi Eko - Biro Transdig UGM** (51:37): Oke, kita cenderung itu dari saya, Mas Alip. Monggo, silakan dilanjutkan.
**Dedi Eko - Biro Transdig UGM** (51:46): Layanan ji nah mungkin saya kasih baca. Mohon izin Pak Farda, mungkin bisa menyampaikan ini yang terkait dengan karena kami di perguruan tinggi, jadi itu ada satu hasil riset yang kita
**Mardhani - Biro Transdig UGM** (52:01): Untuk impact untuk solusi ke masyarakat juga menggunakan AI ini, kebetulan ongoing juga prosesnya. Monggo, Pak Farida, jadi?
**Mardhani - Biro Transdig UGM** (52:44): Terima kasih, Ramonisin, Pak Nadiem, Pak Sves, Pak Tibus, dan para ibu sekalian. Jadi, apa namanya ini tipe?
**Mardhani - Biro Transdig UGM** (52:54): Kondisi saat ini terkait dengan apa namanya bencana, ya kurang lebih semacam itu. Jadi dari sini carannya dari tahun 2006, gitulah. Nah, ini seharusnya satu dari penggunaan EA-nya. Jadi, dia bisa untuk merapikan, jadi kita mungkin.
**Mardhani - Biro Transdig UGM** (53:09): Data-data yang masih lain data seperti itu nanti bisa dianalisis di peta, misalnya dari benteng gitu ya, terus kemudian titik-titik, sisanya, tandukunya segala macam. Tapi ini bisa dinilai kira-kira, yang perlu itu di mana? Terus kemudian.
**Mardhani - Biro Transdig UGM** (53:24): Kemudian itu saya mungkin menginterpretasi rencana di mana kemudian dalamnya juga dia analisis ya, jadi visioning model gitu tadi, mungkin karena yang diberikan begitu ya, data sih ini juga bisa untuk.
**Mardhani - Biro Transdig UGM** (53:39): Dari lembar foto itu bisa terjemahkan dia jalannya bisa dilolongin gitu atau apa yang trans kalau macam emoji ini juga nanti bisa untuk optimasi optimalisasi alatnya jadi misal ketika di situ.
**Mardhani - Biro Transdig UGM** (53:54): Sudah terjadi bencana dan terus kemudian ada hal ini tidak dilalui, bisa dilaluinya? Mungkin apa yang membantu tuanya siapa dan segala macam kurang semacam itu jadi.
**Mardhani - Biro Transdig UGM** (54:05): Kalau tadi mungkin Pak Deddy yang selama ini masalah beberapa mungkin non seperti hal-hal di analisis juga bisa disampaikan di hal itu?
**Mardhani - Biro Transdig UGM** (54:17): Tambah dan segala macam terkait dengan AI-nya, termatem itu simpelnya gitu ini?
**Mardhani - Biro Transdig UGM** (54:23): Jadi, selain proyek apa Tech for Disaster ini, ini benar-benar salah satu apapun flexible research yang kita hilirisasi dan
**Mardhani - Biro Transdig UGM** (54:35): Kita juga belajar memanfaatkan engine-engine AI yang benar-benar industri kritis. Nah, bulan kita ada kerjasama dengan satu perusahaan itu didukung sehingga untuk melak
**Mardhani - Biro Transdig UGM** (54:47): Kemampuannya cukup luar biasa. Jadi, nanti pada level tertentu, sepertinya memang cukup serius. Misalnya, pemerintah harus apa ya punya kita mengikap kalau kami di perguruan tinggi kan budget terbatasi.
**Mardhani - Biro Transdig UGM** (54:59): Jadi kalau pemerintah itu bisa menyediakan buatnya luar biasa sekali, selain effort disaster, kami juga punya Smart Agriculture. Ini juga digunakan untuk otomatis irrigation sistem.
**Mardhani - Biro Transdig UGM** (55:10): Monitoring plantation dan seterusnya ini juga sudah running di beberapa daerah.
**Mardhani - Biro Transdig UGM** (55:17): Ini dan yang terakhir itu nanti ada Inus TPI, jadi untuk daerah-daerah terluar di Indonesia itu akan diberikan alat. Mungkin Bapak Ibu masih ingat, Bu, jenis yang untuk COVID yang takutnya?
**Mardhani - Biro Transdig UGM** (55:40): Tidak terluar.
**Mardhani - Biro Transdig UGM** (55:42): Cukup alatnya itu, tapi nanti dia akan melempar data screening-nya itu ke ke lokal gitu, kemudian disinkronisasi ke apa namanya?
**Mardhani - Biro Transdig UGM** (55:52): Ke data center juga. Nah, ini juga menarik karena nanti bisa menyelesaikan permasalahan di masyarakat. Selain itu, sambil screening, itu kita pun dapat database daerah, ya, karena ternyata
**Mardhani - Biro Transdig UGM** (56:03): ini.
**Mardhani - Biro Transdig UGM** (56:04): Demografi daerah itu mempengaruhi perubahan data modelnya, jadi bedah-bedah nanti tipe Jawa, tipe di Sumatera, apalagi ini pas sebenarnya ya ada kebakaran hutan.
**Mardhani - Biro Transdig UGM** (56:15): Itu kan efek, salah satu efeknya kan di pernapasan ya, itu bisa menjadi sesuatu yang sangat berat. Cuma nih, obstacle-nya satu, Pak, karena afretnya luas konektiviti?
**Mardhani - Biro Transdig UGM** (56:26): Ini problem kita. Kita lagi mencari industri yang punya jangkauan konektiviti yang masif.
**Mardhani - Biro Transdig UGM** (56:33): Gitu, nah, ini yang jadi masalah. Jangan sampai terpaksa starling kalau bisa, ya, yang ada di kita karena datanya sangat berat sekali. Ji, mungkin itu overview-nya, Bapak, Ibu. Mungkin dari teman-teman BTD, ada yang ingin menyampaikan lagi?
**Mardhani - Biro Transdig UGM** (56:48): Iwan Kurisir, ada tambahan mungkin?
**Mardhani - Biro Transdig UGM** (56:52): Halo, baik, mungkin seperti itu, Pak Yunus. Kami persilakan kembali. Mungkin ini kita bisa diskusi dan juga memperdalam apa yang sudah kami coba sampaikan.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (57:03): Ambil di lihat-lihat gitu ya. Terima kasih, terima kasih Pak Karo, Pak Mardani, serta rekan-rekan dari Biro Transformasi Digital UGM. Jadi, ini mau izin juga nih, saya sudah hadir, Pak Marhudi. Nanti mungkin kami mohon perkenan saya menyampaikan beberapa.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (57:18): Hal yang kami laporkan tadi, Pak Sersami, di awal sudah sampaikan ke Pak Mardhani, kepada Kakro, bahwa Bappenas dispesifik dari unit Sekretariat Departemen Perencana Makro itu melihat perkembangan saat ini memang dengan banyaknya data.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (57:34): Yang kondisinya hampir sama, makanya di UKM juga ada silo antar direktorat dan mereka mengerjakan banyak hal, tapi kalau ini terus polain seperti ini menjadi tidak efisien karena
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (57:46): Di level kebijakan, tentu saja Bapak Deputi kami, bahkan Bapak Menteri, nanti akan membutuhkan waktu dan juga belum ada yang bisa menjamin apa namanya?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (57:58): Bahwa apa yang sudah dihasilkan itu memang betul-betul yang paling katanya kalau Pak Saz menggunakan bahasannya single source of truth, nah AI ini membantu.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (58:09): Ya, membantu karena kapasitas human kan terbatas, Pak. Nah, ini tadi Pak Karo juga sampaikan sepertinya kerja sama dengan kementerian dan lembaga sudah mulai saat itu.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (58:21): Minimal dengan kombij tadi, seperti untuk apa namanya, media monitoring seperti itu dulu. Kami di Bappenas pernah juga, Pak, dengan bentukannya big data-nya word.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (58:33): Bank itu jadi dulu salah satu yang dipakai tuh, tapi waktu itu hanya Twitter, Pak. Jadi ada, misalnya, model terkait dengan prediksi inflasi kalau misalnyah Kementan.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (58:45): Perdagangan punya data statistik resmi dari harga komoditas seperti itu. Nah, ini dicoba dulu ditarik data dari Twitter kalau itu bisa mencerminkan, artinya pemerintah sudah tahu lembaga keu
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (58:57): Dulu di provinsi mana yang kira-kira kemungkinan bakal ada kenaikan harga, belum data resmi dari pegangan keluar? Nah, ini kan mungkin juga hal-hal seperti ini, kami di Bappenas sudah mungkin bisa juga.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (59:09): Nanti mau bekerja sama dengan UGM, Pak, karena apa namanya, di tempat kami ada direktorat-direktorat terkait dengan perencanaan ekonominya. Aktu itu keterkaitannya dengan
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (59:21): Proyeksi pertumbuhan ekonomi dan pengawalan pertumbuhan, Pak Nah. Pengamatan pertumbuhan ini kan sebetulnya leading indicator-nya itu kan di aktivitas ekonomi masyarakat. Nah, sebetulnya ada nggak apa namanya word of cloud?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (59:33): Nya, kalau bisa mencerminkan ekonomi masyarakat, tuh ada nggak? Itu kan sebetulnya menarik juga untuk melihat satu daerah atau satu wilayah itu ternyata leading indikator ekonomi untuk katakanlah konsumsi masyarakatnya tinggi, sehingga kemungkinannya besar.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (59:45): Dia PDB provinsi itu nanti mungkin di triwulan depan akan naik seperti itu. Nah, hal seperti ini yang tentunya di luar yang sudah sekarang sedang
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (59:57): Kami kembangkan, tentu saja ini perlu banyak masukan dari otoritas. Pak, tadi Bapak sampaikan juga dulu bergeraknya belum dengan regulasi, tapi saya tadi melihat di awal paparan Bapak bahkan.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (60:09): Sekarang apa namanya dari biro Pak Madani sudah membuat satu etika, ya, kode etik untuk pemanfaatan AI. Nah, mungkin nanti di tingkat kami juga, apakah perlu juga mengatur hal-hal seperti itu?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (60:25): Nanti harus kami lihat, Pak, apa namanya implementasinya. Nah, kira-kira kami berterima kasih, Pak. Tadi apa namanya, banyak hal potensi untuk pengembangannya, tapi kita mau
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (60:36): Senang, Pak Ses, untuk menyampaikan sepatah dua kata, Pak, terkait dengan hutan kita. Terima kasih, baik-baik.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (60:44): Terima kasih. Assalamualaikum warahmatullah wabarakatuh. Yang kami hormati, Pak Madani, Pak Karu Biro Transformasi Digital dari UKM ini.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (60:58): Lama-lamanya ini mau apa, Pak? Ini terus tadi orang di sana ada acara forum masyarakat statistik. Dinamannya Grand Mercury sama Pak Deputi dan beberapa ibu-ibu anggota FMS. Jadi, kami tadi agak telat mengikutin dulu sebentar di sana lalu.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (61:13): Ini saya sampel di jalan, Pak Madani, mengikuti paparan Bapak gitu sambil di jalan. Saya langsung, ini yang ingin pingin nih, Pak. Jadi ditambah tadi ya, pekerjaan penulisan dari apa namanya, Pak Ali, kemudian Pak Netti?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (61:28): Iya tadi dan tadi yang tentang apa namanya kompetitifisien atau visinya AI ya tadi?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (61:34): Semakin menguatkan ini, Pak, apa namanya, niat sebenarnya? Jadi kalau kami boleh cerita, Pak Mardhani, Bapak, Ibu, Sekretaris di UGM ini.
**Pak Ewin - Sesdep PMP** (61:46): Emang ini kami unit baru, Pak. Benar-benar unit baru, beneran unit baru, gitulah sebutannya. Baru, tapi sudah ada dari pecahan sebelumnya itu. Tapi unit yang kami ini, unit
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (61:57): Baru ada tugas Tata Kelola, di situ ada tugas Pengeluaran Data dan Informasi, Pak?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (62:03): Sehingga masih belajar lah ini, Pak, karena dia masih belajar. Tapi kemudian kami menyadari gitu, Pak, saya personal gitu ya, sebenarnya banyak ruangan untuk kita apa namanya menjadi lebih baik, terutama
**Pak Ewin - Sesdep PMP** (62:17): Yang setiap hari kita baca beritahape itu scroll-scroll, tuh ini kok?
**Pak Ewin - Sesdep PMP** (62:22): AI, AI, dan apalah teknologi digital lah secara keseluruhan itu kok?
**Pak Ewin - Sesdep PMP** (62:27): Sudah semakin masif gitu kan ya, Pak? Pilihannya ya kita mau bisa tapping benefitnya dan menjadi bagian dari arus itu, atau ya udah kita kembali ke cara-cara konvensional tradisional tapi tergilas kita gitu, kan ya, Pak? Karena kami menyadari pendatang yang paling sederhana.
**Pak Ewin - Sesdep PMP** (62:43): Apa, Pak Karo? Pak Madani, ini saya sudah sempat dibikinkan paparan tentang apa gitu ya, Pak? Tentang sesuatulah. Ya, bikin paparan itu dari temen-temennya. Sebulan lagi saya mau cari. Itu sudah susah sih, Ba.
**Pak Ewin - Sesdep PMP** (62:54): Saya entah lupa judulnya, saya entah lupa Entah lu kontennya, tapi saya lupa ditaruh di paparan yang sebelahan mana, kan simpel sekali gitu ya, Pak? Tapi itu sudah makan waktu saya untuk mencari.
**Pak Ewin - Sesdep PMP** (63:06): Tuh ya, Pak, ini sebenarnya saya refleksikan itu, ya harusnya kita bisa dibantu dengan teknologi yang begitu besar.
**Pak Ewin - Sesdep PMP** (63:13): Ditambah lagi dengan banyak pekerjaan-pekerjaan yang sebenarnya, ya, jangan terlalu banyak kita menghabiskan waktu di situ, gitu, Pak, sehingga banyaknya nanti dia aspek-aspek kan sifatnya analisis pagi tadi saya.
**Pak Ewin - Sesdep PMP** (63:24): Ing, ingat kata-kata Bapak bahwa dashboard itu kan dashpot, misalnya ya, Pak, bukan hanya data-data yang harusnya bisa memberikan insight, gitu ya, Pak? Harusnya bisa memberikan sesuatu untuk orang mengambil keputusan atau melihat secara
**Pak Ewin - Sesdep PMP** (63:36): Utuh gitu ya? Jika memungkinkan, kan berarti apa foresight itu, Pak, dari apa yang terjadi saat ini? Ini kami sebenarnya ingin belajar, Pak Padani, dan jika memungkinkan, mungkin
**Pak Ewin - Sesdep PMP** (63:47): Apa namanya, mungkin dengan cara seperti apa, dengan pembahasan apa namanya, sumber daya yang ada atau pola hubungan yang dapat kita bangun, Pak? Mungkin ya, kami berharap kita bisa ini, Pak, melanjutkan. Ini kan masih bersamaan.
**Pak Ewin - Sesdep PMP** (64:00): Paking awal itu apa? Kami sudah ini luar biasa sekali kalau saya melihat sendiri, mungkin ada yang levelnya nanti harus dilevel Bappenas secara keseluruhan, Pak. Jadi misalnya area bermainnya tadi, Pak.
**Pak Ewin - Sesdep PMP** (64:12): Jadi ya area bermainnya dengan Hermes dan sebagainya itu mungkin ada tataran yang butuh, mungkin butuh infrastruktur digitalnya lebih cukup ngsip gitulah, Pak Joko.
**Pak Ewin - Sesdep PMP** (64:24): Bagus gitu ya, tapi mungkin kami, nah ini masalahnya kan, Pak, ada di level yang kementeriannya secara keseluruhan yang dia namanya butuh polisi?
**Pak Ewin - Sesdep PMP** (64:35): Keseluruhan gitu ya, Pak, tapi mungkin?
**Pak Ewin - Sesdep PMP** (64:39): Butuh waktu untuk apakah mereka mau? Apakah mereka sudah berdata inline, Pak, di rencana strategisnya? Walaupun nanti tentu kami akan memberitahukan gitu, ya, itu mungkin dimulai, bisa dimulai dari kami, Pak, yang kita mulai hal-hal yang sederhana.
**Pak Ewin - Sesdep PMP** (65:04): Sekali tadi yang disampaikan di belakang ini, malah kalau APBN atau akuntan tuh jadi proses engineering bikin-bikin sendiri gitu ya? Ya sebenarnya kan sudah lebih gampang kita di era saat ini.
**Pak Ewin - Sesdep PMP** (65:16): Ini kita tinggal kalau saya melihat yang tata kuncinya adalah mungkin brand design besarnya Pak Mardhani Maslo. Sebenarnya kalau di level kami gitu ya, di apa namanya?
**Pak Ewin - Sesdep PMP** (65:28): Deputasi tertentu dengan tugas tertentu gitu, Pak. Ada layanan, ada produk yang harus dihasilkan, adalah yang harus disampaikan. Ada yang tugas-tugas itu terpecah-pecah, terbagi-bagi ya, Pak. Dan sekarang sudah selesai?
**Pak Ewin - Sesdep PMP** (65:40): Bekerja sudah punya kayak semacam tersebut, masing-masing sudah punya, masih modeling masing-masing gitu ya, tapi apakah bisa dalam satu?
**Pak Ewin - Sesdep PMP** (65:53): Integrasi yang sama untuk memberikan insight tadi ya, atau memberikan foresight kepada pimpinan secara akurat dan tadi bisa dipercaya gitu kan, Pak? Setnya tuh apakah bisa?
**Pak Ewin - Sesdep PMP** (66:04): Mungkin Pak, kita saat ini sehingga kami melihat nanti kalau misalnya mau kita mengembangkan, ya?
**Pak Ewin - Sesdep PMP** (66:11): Dalam bangkah setahun apa yang kita bisa lakukan? Nanti Pak, dua tahun, tiga tahun, lima tahun, gitu apaan bisa dilakukan? Kami mungkin mohon-mohon dibantu gitu, Pak, atau kita berkolaborasi karena Bapak ini kalau
**Pak Ewin - Sesdep PMP** (66:22): Dan ini sudah sangat advance dia dengan segala produknya, bahkan yang luar biasa yang terakhir Bapak sampaikan, ya ujung-ujungnya kan berdampak, ya Pak. Ujung-ujungnya yang dia sudah langsung hilirnya langsung ke masyarakat.
**Pak Ewin - Sesdep PMP** (66:34): Itu sebenarnya yang diharapkan dari pemerintah, Pak, walaupun kami bukan yang sifatnya fisik yang menghasilkan hal tersebut, tapi kajian analisis ekonomi disampaikan oleh Pak Yunus tadi tentang inflasi dan sebagainya, ya, kalau bayangkan.
**Pak Ewin - Sesdep PMP** (66:58): Torat sektor gitu ya, Pak. Direktorat yang menghasilkan produk itu, tuh, tugas kami. Terus ini menyediakan platformnya, menyiapkan jalannya, sehingga ini kita secara ini melangkah kecil-kecil, ini kita bisa.
**Pak Ewin - Sesdep PMP** (67:10): Capai ke depan gitu ya, Pak? Apapun kan bisa dari biasanya kalau
**Pak Ewin - Sesdep PMP** (67:14): Apa namanya infrastruktur teknologi ini kan biasanya cepatnya ya, Pak, berubah-nyakit banyak. Mungkin kalau misalnya kita, kami mau mengembangkan nih, misalnya nanti ada masukan dari Bapak gitu, ya, sekalian yang biar nanti sudah.
**Pak Ewin - Sesdep PMP** (67:28): Tidak setara dengan itu, kan sulit gitu, Pak. Sudah harus merubah lagi, gitu. Kan berarti kan ada punya yang juga sudah harus dipikirkan dari sekarang, gitu, Pah?
**Pak Ewin - Sesdep PMP** (67:38): Mungkin karena?
**Pak Ewin - Sesdep PMP** (67:39): Nah, ini mungkin saya sampaikan, Pak Inos juga sudah beberapa kali, Pak, lah kecilnya sudah coba dikembangkan juga oleh teman-teman. Basisnya pertama, saya melihat ini kan banyak sekali, Pak. Ini
**Pak Ewin - Sesdep PMP** (67:51): apa eh pem?
**Pak Ewin - Sesdep PMP** (68:03): Bagus, kita saat ini tuh dianggap yang apa, sudah selesai dilaporkan itu simpan nih, Pak? Simpan berarti kan tidak, di situ ada buah pikirnya, di situ ada analisisnya, gitu, yang sudah dipurasi, gitu kan, Pak?
**Pak Ewin - Sesdep PMP** (68:15): Yang sudah dikurasi, sudah dipastikan kebenarannya oleh direktor tersebut, menyampaikan dari putih itu, saya bilang, "Ya, ini luar biasa sekali," gitu kan. Jadi, di tahap pertama, banyak sampaikan teman-teman kemarin kalau bisa, ya, jadi apa yang ada?
**Pak Ewin - Sesdep PMP** (68:39): Pak, ini masih... Ini Pak bertanya, Pak, terus hati-hati nih, jangan pake yang token kayak punya waktu, tapi belum ini, apa masih sangat-sangat embrio? Tapi tadi kami ingin bisa memulai.
**Pak Ewin - Sesdep PMP** (68:51): Pak Mardhani bisa memulai sehingga kita nggak ketinggalan dan sebenarnya pada ujungnya memanfaatkanlah era ini biar kerja kita lebih efisien. Saya bilang ke temen-temen, gabut kita lebih nyaman di situ aksi itu.
**Pak Ewin - Sesdep PMP** (69:03): Nah, nggak perlu semuanya terpusat. Ada sesuatunya yang sebenarnya kita bisa otomasi, kita bisa lakukan remote, kita bisa melakukan sudah langsung jalan aja gitu. Bahkan ini kan waktu-waktu kita, ya?
**Pak Ewin - Sesdep PMP** (69:27): Kenalnya Pak Adiprasdi, kami senang sekali ini bisa bicara langsung nih dengan Bapak. Mungkin kita izin nanti, mungkin langkah berikutnya kita tindak lanjuti. Ini tentu kami akan sangat terima kasih kali, Pak Muhammad, dan pula.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (69:39): Terima kasih, Pak Dewan Transmisi Digital UGM. Terakhir, Pak, awalnya balikan ke Pak Yunus. Terima kasih saya atas apa namanya, beberapa hal yang perlu jadi catatan kami juga kan nanti di tingkat teknis untuk.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (69:51): Diskusi ini sesuai jadwal kita hari ini ada sesi kunjungan dan pembelajaran pengembangan pelatihan dari esbatu GM nih. Mau izin Pak Karo, berarti di tempat ini atau di tempat?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (70:03): Apart lain di sini juga baik, mungkin sebelum sampai ke sesi tersebut, kami juga mempersilakan rekan-rekan untuk bertanya. Mungkin ada Pak Karo, jadi teman-teman di sini juga mungkin ada.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (70:15): Tadi tengah timnya untuk nanya, walaupun saya lihat di belakang udah mulai nanya dulu, jadi saya nggak tahu apa perlu dibuka lagi sih. Kita yang jawab hanya sudah nanya langsung. Jadi memang untuk pengembangan ayang.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (70:27): Dana sederhana, sepertinya Pak Deddy menginspirasi tadi. Kalau di kami kan ada direktorat yang harus menyampaikan pertanggungjawaban perjalanan dinas, apa itu bisa otomatis nanti? Terus kemudian ada direktoratnya.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (70:38): Karena naskah dinas itu apa juga mungkin bisa diotomatis sekaligus ditarik datanya, terus diekualifikasi pergerakannya, gitu. Mana perginya, ke mana aja sih orang-orang? Mending menarik juga untuk bisa melanga ke situ.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (70:50): Menggoh, Mas Adit, kalau ada yang mau ditanya ke Pak Karo, silakan, Mas Adipuluh.
**Grady - Sesdep PMP** (70:58): Oke, izin, terima kasih, Pak Jonas. Mohon izin, Pak Ses Pagaruk. Izinkan, Mas, sebenarnya cukup menafik tadi, saya juga semuanya menggunakan router, Pak, untuk ini apa namanya, ya?
**Grady - Sesdep PMP** (71:08): AI dan lain sebagainya, namun memang untuk dengan untuk peding seperti yang tadi, sepertinya model China bahkan aman lebih murah, nah.
**Grady - Sesdep PMP** (71:20): Tapi untuk yang ada di playground-nya, karena itu aksesnya adalah data yang memang dibapenas, ya, Pak, dan sebenarnya kalau dilihat mau dekat?
**Grady - Sesdep PMP** (71:32): Cina ini belum ada zero data retention yang menjawabkan kami agak takut nih menggunakan model China, walaupun sebenarnya kalau kita bicara konversinya lebih murah, nah tapi setelah melihat.
**Grady - Sesdep PMP** (71:44): Tadi di apa namanya dashboard yang DST itu ada penggunaan kwen juga. Nah, itu yang merupakan model China juga. Nah, itu bagaimana concern terkait dengan?
**Grady - Sesdep PMP** (71:56): Apa namanya zero data retention-nya, Pak? Keamanan datanya ini, Pak?
**Mardhani - Biro Transdig UGM** (72:01): Baik, terima kasih. Pada tahap awal, Pak, biasanya kami memang strateginya itu mau tidak mau karena kita belum, waktu dulu ya, kata-kata masih juga learning, gitu.
**Mardhani - Biro Transdig UGM** (72:14): Akhirnya aspek keamanan data itu sedikit banyak kita ulur gitu, kita urut tapi dengan mitigasi yang terukur. Makanya kami tadi sampaikan, kami fokus dulu ke dalam.
**Mardhani - Biro Transdig UGM** (72:26): Data yang memang sifatnya publik, dari public itu ya memang sudah viable di internet, atau mungkin di website-nya masih-muasi Juli kerja, tapi masih sketer atau belum. Tadi disampaikan Bapak, tadi belum.
**Mardhani - Biro Transdig UGM** (72:38): Bisa diambil sinergisnya, nah, sehingga ketika kita mengolah itu, ya, kami juga bekerja sama dengan teman-teman yang menjalankan pengelolaan informasi publik di kami.
**Mardhani - Biro Transdig UGM** (72:50): Kami mendapat irans bahwa itu oke, ya udah gitu bisa kita lakukan. Tujuannya apa? Tujuannya untuk mengetes model mana yang paling
**Mardhani - Biro Transdig UGM** (72:58): Baik, kiri ya. Nah, ternyata kita mendapatkan pada waktu itu masing-masing model itu.
**Mardhani - Biro Transdig UGM** (73:04): Akurat bagus untuk kis-kisis tertentu tidak ada.
**Mardhani - Biro Transdig UGM** (73:10): Apa istilahnya itu, apa ya, satu-satu yang bisa untuk semua begitu? Nah, tuh problem-nya di situ, tapi sebenarnya bukan problema, tetapi malahan kami melihat celah berarti.
**Mardhani - Biro Transdig UGM** (73:20): Kita sudah harus move ini pada tahap tertentu, ingat sendiri. Nah, jadi kami di terus-terang ya, strategi kami adalah memang kami di awal nih emang bayarin token, Mbak, tapi.
**Mardhani - Biro Transdig UGM** (73:31): Kami berharap tokennya, kalau bahasa grafik itu, tidak naik tapi ke zero. Dengan kata lain, kita akan develop sendiri. Kami pakai cara China, Pak, copy. Copy apa namanya?
**Mardhani - Biro Transdig UGM** (73:43): Kopi cat jadi kopi melarir bersendiri. Jadi kita tiru nggak sih? Kita coba bikin sendiri. Nah, jadi semacam itu. Jadi semacam dan itu ternyata bisa. Ternyata bisa. Jadi, Danitu bagi teman-teman.
**Mardhani - Biro Transdig UGM** (73:58): Saya dulu memikirkan gimana caranya agar teman-teman SDM ini, SDM IT ya, terutama itu juga bisa upscale kemampuannya?
**Mardhani - Biro Transdig UGM** (74:06): Kalau kita mau training?
**Mardhani - Biro Transdig UGM** (74:09): Itu kadang kita bisa mentrainingkan, tapi kesempatan waktunya nggak ada karena pecahnya banyak sekali. Nah, akhirnya ternyata dengan cara kita minta untuk bicaraan dengan Inovasi begitulah, itu automatically.
**Mardhani - Biro Transdig UGM** (74:20): Naik WA skill-nya. Nah, jadi contohnya ya, teman-teman, kami itu seperti Mas Deddy tuh mungkin baru setahun di kita, ya, tahun di PT TWA, tapi sudah skill-nya sudah tinggi. Jadi semacam itu yang mungkin itu tidak akan terek
**Mardhani - Biro Transdig UGM** (74:33): Spektrasi kalau kita akan tercapai kalau modelnya biasa, nah kita kemudian membuat mekanisme untuk rekonsiliasi itu, jadi naiklah ke kemampuan dan juga yang lainnya.
**Mardhani - Biro Transdig UGM** (74:45): Nah, jadi itu, Pak, segmennya, sehingga kalau kita melihat nanti berbagai banyak solusi itu memang menggunakan banyak model. Kalau bahasa kami, ya, banyak algoritma yang kita coba dan sehingga kita custom.
**Mardhani - Biro Transdig UGM** (74:57): Karena pada titik tertentu, kami juga memahami, apa istilahnya itu, kita tidak hanya sekadar menanggungjawabkan pada tipe yang tampul, Pak?
**Mardhani - Biro Transdig UGM** (75:09): Tapi bagaimana proses itu berjalan? Jadi nggak boleh ada, kalau saya ya, jangan sampai ada flag fox gitu. Ya, kita nggak boleh jawab algoritmanya. Gitu, kok ini? Itu kan nggak boleh. Tidak harus explain. Gitu ya, iapun.
**Mardhani - Biro Transdig UGM** (75:21): Data masuknya ini, keluarnya ini, prosesnya ini yang dijalankan terus-terusan.
**Mardhani - Biro Transdig UGM** (75:26): Um.
**Mardhani - Biro Transdig UGM** (75:28): Ternyata dengan cara itu kita bisa menghandle banyak isu, misalnya kita diserang, urutan tuh kainya UGM salah, ini kan? Saya jelaskan aja apa secara ilmiah padanya.
**Mardhani - Biro Transdig UGM** (75:38): Ya, jadi semacam itu, bahkan tuh lebih-lebih bisa acceptable ya dibanding yang lain tadi, semua macam itu, Pak. Jadi mungkin poinnya di situ. Nah, sehingga mungkin kalau kami boleh memberikan saran, memang dari sisi pimpinan mungkin membebaskan Nanda Kut.
**Mardhani - Biro Transdig UGM** (75:50): Timnya untuk mengexpasi ruang untuk mengeksplorasi, Pak, kalau boleh, unsur KPI-nya itu berapa? Bukan nilai keberhasilan, berapanya dia melakukan error, Pak? Wah, itu KPI tuh menurut saya jadi.
**Mardhani - Biro Transdig UGM** (76:02): Gitu, jadi kalau KPBI-nya ya gitulah, itu menarik menurut saya. Begitu. Jadi, saya sering itu pakami di pirutan soal logis mengusulkan hal-hal yang aneh-aneh itu di lojangan direkognisi yang berhasilnya, tapi filenya itu dilaporkan. Gitu dari gini. Nah, terantai ya.
**Mardhani - Biro Transdig UGM** (76:17): Ambat laun mungkin agak sulit, tapi ternyata bisa jadi, kira-kira begitu. Nah, saya tadi yang Bapak sampaikan juga tadi strateginya mungkin mirip dengan kami, Pak, ketika memulai dulu. Dua strategi yang kami lakukan, Pak. Jadi, pertama, emang strateginya itu
**Mardhani - Biro Transdig UGM** (76:32): Satu kebijakan kalau saya?
**Mardhani - Biro Transdig UGM** (76:34): Kami tidak akan mengerjakan sesuatu yang sifatnya itu langsung besar gitu, Pak, tapi kecil tapi terus ada kerut-nyanya, kadang-kadang mentok, Pak.
**Mardhani - Biro Transdig UGM** (76:45): Dengar viral bahasa sepak bola, saya pindah ke kiri gitu, kanan, kadang terpaksa begitu. Itu biasanya, tapi gitu. Tapi intinya baby step. Kemudian yang kedua itu kami.
**Mardhani - Biro Transdig UGM** (76:57): Ini lebih banyak mencoba untuk menghadirkan apa namanya itu?
**Mardhani - Biro Transdig UGM** (77:02): Working with example gitu, jadi ini bentuknya kadang begini, Pak, terutama kalau di kampus ya. Kalau kita mengusulkan sesuatu, rapatnya itu bisa dua bulan, Mbak.
**Mardhani - Biro Transdig UGM** (77:14): Dan itu setiap rapat kembali ke titik nol, berarti ya, jadi sampai saya tuh sampe beberapa kali waktu dulu Pak menolak untuk hadir rapat. Dek, nggak mau lah kalau rapatnya kayak gini terus, gitu. Jadi mending saya kasih waktunya kerjain dulu.
**Mardhani - Biro Transdig UGM** (77:27): Saya mending bawa rapat, tapi kayak ujian presentasi itu, Pak Jody dibantai gitu, malah lebih seneng daripada. Tapi jadi kebiasaan sekarang, setiap rapat saya yang dibancai mudanya.
**Mardhani - Biro Transdig UGM** (77:39): Nah, itu yang menarik.
**Mardhani - Biro Transdig UGM** (77:41): Tapi tidak apa-apa, itu proses. Jadi, saya setuju nanti strateginya begitu. Dan nanti kalau orang sudah bisa mengok ke tempat bawa yang di unit ini, saya pikir tuh, kalau bahasa siwanya Pak Betularnya tu lebih ampuh, gue ide ya. Jadi lebih terasa, tinggal replikasi.
**Mardhani - Biro Transdig UGM** (77:57): Itu sih maksudnya?
**Mardhani - Biro Transdig UGM** (78:00): lihat.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (78:03): Terima kasih, Pak Karo, Mas Sadit. Kalau masih ada pertanyaan lain, rekan-rekannya juga?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (78:09): Kami persilakan.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (78:12): Ketahuan juga ya? Jadi, Pak Karo, kami juga sebetulnya ini ada menggunakan Zoom, di online hadir juga rekan-rekan dari pusat data informasi apa perencanaan pembangunan, jadi mungkin kalau
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (78:26): Kalau dari online ada pertanyaan yang apa namanya akan disampaikan, monggo. Nah, nanti kita juga dalam pengembangannya ini kami di keributan PMP akan.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (78:38): Berkolaborasi terus dengan rekan-rekannya musdatif. Jadi, kalau rekan-rekan Pusdati juga ada yang ingin ditanyakan, kami persilakan.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (78:48): Terutama pengembangan AI di tingkat lembaga, ya, nanti untuk siap.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (78:53): Aduh! Kalau misalnya kayak gitu kan?
**Mardhani - Biro Transdig UGM** (78:57): Awasin mereka sih.
**Mardhani - Biro Transdig UGM** (78:59): Oke, stop iklim. Oke, stop. Terus kan traffic jam?
**Mardhani - Biro Transdig UGM** (79:04): Lagi sekolah deh, udah berangkat sekolahan.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (79:07): Sudah merdeka kalau di kami berangkat sekolah mungkin tinggal ambil istri tiga tahun ya seneng iya nih. Kami persilakan rekan-rekannya yang hadir di online.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (79:21): Dan apabila ada yang ingin didalami terkait dengan pemanfaatan kecerdasan buatan untuk mendukung pengambilan kebijakan di kantor itu?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (79:31): Tingkat lembaga atau mungkin ada perwakilan dari direktorat juga yang ingin bertanya terkait potensi pengembangannya di sektornya masing-masing?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (79:40): Ada dari Direktorat Tingkatan Produktivitas, Mas Mangunbo. Jadi kalau ada yang mau ditanyakan, Asmista Mangun. Iya, Pak. Izin, Pak, perkenalkan nama saya Miftah dari Tirta.
**Audiens** (79:51): Peraturan yang batet izin pertanyaannya nanti tadi kan dari UGM akan mengembangkan model AI sendiri ya, Pak. Ya, nah itu ke depannya apakah nanti stay open source atau close share biar bisa diadopsi ke KL ataupun peraturan lain gitu?
**Mardhani - Biro Transdig UGM** (80:06): Oke, ini sambil masuk ke sesi yang tersebutnya. Oke, Mas Alih bisa tampilkan yang DTs Lab, yang analitik imutek gitu, salah satu?
**Mardhani - Biro Transdig UGM** (80:18): Jadi ini use case-nya memang sekaligus menunjukkan, Pak. Jadi mungkin sebelum-sebelum ke situ, saya mau izin sekali nih untuk menjelaskan. Mungkin kembali ke dashboard UKM dulu, dashboard UKM dan support satu KM, Pak Sety. Jadi saya tunjukkan dulu, Bapak, Ibu, jadinya.
**Mardhani - Biro Transdig UGM** (80:31): Ini adalah tampilan dashboard UGM yang bukan kami yang menghasilkan, tapi yang dihasilkan adalah Direktorat Teknologi Informasi karena direktorat inilah yang menjadi penguasa sistem informasi.
**Mardhani - Biro Transdig UGM** (80:46): Dan data primary yang ada di universitas, jadi mereka secara apa, bertahap atau batch gitu, dia mengupdate data-data, baik itu tentang ini untuk kepalan publik nih. Jadi sejari sesuai dengan tag-nya ya, UGM dalam angka.
**Mardhani - Biro Transdig UGM** (81:01): nah.
**Mardhani - Biro Transdig UGM** (81:02): Ya, ini hanya diskusi biasa, tapi karena kita sudah establish, maka kami berpikir bahwa kalau ini oke, ini untuk misalnya untuk, ya, semacam kunjungan, tapi yang sifatnya hanyalah ingin
**Mardhani - Biro Transdig UGM** (81:16): Melihat profilnya UGM gitu menarik, ya, tapi ternyata dalam kenyataannya, Bapak, Ibu, dalam level tertentu, terutama untuk mungkin Bappenas punya DNA yang hampir sama dengan perguruan tinggi, ya. Ajian selotijek-nya kan kuat, ya. Nah, kami juga berpikir yang sama, Mbak.
**Mardhani - Biro Transdig UGM** (81:31): Terkait dengan untuk mendukung kita agar bisa, apa namanya, naik peringkat internasional dan seterusnya, misalnya gitu. Jadi, nah, kemudian kami menghadirkan satu pelat.
**Mardhani - Biro Transdig UGM** (81:43): Platform khusus yang kami sebut sebagai data analitik, nah itu mungkin yang ke DTS-nya, yang keempat juga.
**Mardhani - Biro Transdig UGM** (81:50): jadi.
**Mardhani - Biro Transdig UGM** (81:53): Nah, di sini di salah satu senbok kami itu, kami punya.
**Mardhani - Biro Transdig UGM** (82:00): Data analitik yang terkait dengan.
**Mardhani - Biro Transdig UGM** (82:04): Kemudahan?
**Mardhani - Biro Transdig UGM** (82:06): Nah, kenapa kami buat ini, mungkin sama seperti Bapak/Ibu di KL, ya. Kami punya juga punya mandat untuk memb berkontribusi. Memang tidak berkonsultasi, memang tugasnya untuk mendukung.
**Mardhani - Biro Transdig UGM** (82:19): Kemendiklat Tinggi dan Tiba-Tinggih dan Resep kira-kira begitu? Nah, kami selalu diminta, Pak, pertanyaannya itu kalau dulu indikatornya kan SDGs. SDGs masih ada.
**Mardhani - Biro Transdig UGM** (82:31): Nah, kami masih punya, jadi mungkin dicoba kalau balik lagi ke dashboard, lah. Yang ke dashboard SDG, sektorinya pindah ke SDG. Nah, ini kami juga punya, Bapak, Ibu. Jadi, ini yang SDG sini.
**Mardhani - Biro Transdig UGM** (82:54): Kegiatannya sendiri?
**Mardhani - Biro Transdig UGM** (82:56): Itu kan biasanya kalau diminta bikin laporan susahnya minta ambun, ya kan sulit gitu, Pak. Saya sendiri juga merasakan kalau udah saya melakukan sesuatu itu.
**Mardhani - Biro Transdig UGM** (83:05): Kalau curuh bikin laporan tuh seperti siksaan tersendiri itu, Pak. Jangan semuanya gitulah. Nah, sehingga yang kami lakukan selanjutnya adalah berarti bukan pelakunya yang membuat laporan, tapi pihak lain, dalam hal ini malah membuat news.
**Mardhani - Biro Transdig UGM** (83:18): Artikel berita yang mengekspos tentang kegiatan itu, nah, itu ditampilkan di banyak sekali website. Nah, kemudian kami mapping, Bapak, Ibu.
**Mardhani - Biro Transdig UGM** (83:28): Kami mapping berdasarkan indikator SDG's, nah sehingga dengan kata lain kami bisa.
**Mardhani - Biro Transdig UGM** (83:36): Ikan informasi kepada kementerian bahwa UGM kita SDGs-nya seperti ini, kontribusi kami misalnya terkait dengan SDGs, terutama ya pendidikan itu. Ya, memang itu tugas kami loh.
**Mardhani - Biro Transdig UGM** (83:48): Akhir-akhirnya begitu ya, jadi seterusnya. Jadi semacam itu, cuma ternyata ini juga curhat dikit yah, kementerian itu kadang suka-suka ganti, Pak, temanya gitu. Ya, terus kemudian
**Mardhani - Biro Transdig UGM** (84:00): Menterinya ganti, sekarang temanya adalah.
**Mardhani - Biro Transdig UGM** (84:03): Pus berdampak aja deh. Kata kunci berdampak ini lah yang kemudian kami diminta untuk mengubah, atau bukan mengubah, tapi mencoba menganalisis ke sana. Nah, dulu yang namanya dulu kan misalnya model ada Kamodel ataupun
**Mardhani - Biro Transdig UGM** (84:18): Algoritmanya itu SDGs sekarang dampak. Nah, ini yang terus menjadikan kami berpikir, ulangkan, ini kalau pendekatannya kami harus bikin sistem baru.
**Mardhani - Biro Transdig UGM** (84:42): Resdampak tadi?
**Mardhani - Biro Transdig UGM** (84:43): Nah, mungkin trennya ke situ, Pak. Jadi, trennya kita akan mencoba sebanyak mungkin mengubah dari sport yang sifatnya itu by number itu berubah.
**Mardhani - Biro Transdig UGM** (84:53): Menjadi insight atau data analitik. Nah, itu seperti ini. Nanti coba ditunjukkan satu sampel, Mas Remis ya, Mbak, gitu. Ya, nah, ini sama seperti
**Mardhani - Biro Transdig UGM** (85:05): Sumbernya sama dengan SDG's tadi, Bapak, Ibu, tapi kemudian ini kebetulan timnya Mbak Putri di belakang, ya. Itu ini kami minta khusus untuk melakukan kerjain Mbak Kiranya?
**Mardhani - Biro Transdig UGM** (85:17): Kira untuk mengeksekusi sumber berita yang sama, tapi ini masih kajian ya. Jadi, kita ambil data sampel dulu, nggak semuanya dulu. Itu bagaimana caranya? Algoritma atau data model seperti apa yang bisa untuk melakukan?
**Mardhani - Biro Transdig UGM** (85:29): Learning untuk menampilkan sesuai dengan kriteria dampak. Nah, kriteria dampak itu dari Kemendes. Ya, kalau Kemendes tuh kan perlu tahu pemerintahan. Saya, Pak, itu sukanya ribet, Pak, syaratnya tu.
**Mardhani - Biro Transdig UGM** (85:41): Kalau nggak mencapai angka seratus, itu tampenya enggak puas mereka. Jadi, mungkin kok gajinya wah? Jadi urusan-urusan tangsang ya. Urusannya kayak begini aja ribetnya, minta maaf nih, nah.
**Mardhani - Biro Transdig UGM** (85:52): Kita kan harus mikir loh ya, ini kalau suatu saat nih nyelip indikator berbeda?
**Mardhani - Biro Transdig UGM** (85:57): Kalau harus kalau kita coding besar gitu ya? Coding langsung itu ngubah kan, ya teman sejukkan misalnya begitu, dan pada Gitulah yang terus jadi dinamik. Nah, akhirnya kita itu masih ongoing ini, Alhamdulillah, sudah.
**Mardhani - Biro Transdig UGM** (86:11): Mulai muncul.
**Mardhani - Biro Transdig UGM** (86:13): Algoritma yang bisa digunakan untuk itu? Nah, itulah jadi kuncinya di situ. Nah, jadi kami menggunakan model dengan seperti itu. Nah, kemudian tapi tidak berhenti hanya sekedar mapping saja atau mungkin saja, tetapi juga menarasikan, ini kan.
**Mardhani - Biro Transdig UGM** (86:29): Itu data model. Nah, kira-kira begitupun ini yang menjadi.
**Mardhani - Biro Transdig UGM** (86:33): Tantangan? Kalau pertanyaannya tadi open source apa tidak untuk stage saat ini, memang kami masih dalam track uji coba, itu belum berani untuk kita opentan. Kita masih coba karena begini, bagi kami tuh seperti itu-tu saya.
**Mardhani - Biro Transdig UGM** (86:48): Apa namanya?
**Mardhani - Biro Transdig UGM** (86:49): Rumus masakan itu benar rumusan masing-masing, tapi bukan ingredients-nya, Pak. Tapi auto cook-nya. Nah, itu pun nggak bisa direplikasi ya. Mungkin sama-sama, misalnya Bappenas kita sama-sama harus berdampingan tadi. Tetapi algoritma behind dampaknya universitas dengan Pak Benang.
**Mardhani - Biro Transdig UGM** (87:04): Mungkin difference, nah itu yang harus dipindahkan, tapi secara teknis nanti kalau misalnya ini direplikasi dan tinggal ditutup, sangat possible kan gitu. Jadi itu, jadi mungkin?
**Mardhani - Biro Transdig UGM** (87:16): Kesalahan kita, Bapak, Ibu, mungkin terkait apa dengan pertanyaan pertama tadi, model China, kenapa tidak begitu bagus? Karena kita banyak mak es?
**Mardhani - Biro Transdig UGM** (87:26): Gitu kan, jadi es-es gitu. Jadi yang kalau motor itu di-tune up dulu, gitulah, ini semacamnya tuh di-fitting. Kalau biasanya, nah itu sebenarnya atau dicek parameternya yang lebih tepat dan seterusnya. Nah, ini yang
**Mardhani - Biro Transdig UGM** (87:38): Kami lakukan, jadi ini salah satu bentuk, Pak. Jadi, geser dari perubahan dashboard by number menjadi analitik tadi, seperti itu. Tidak hanya mungkin levelnya nanti tidak hanya sintesis.
**Mardhani - Biro Transdig UGM** (87:52): Tapi benar-benar menampilkan insight apa semacam itu dari sehingga nanti otomatisasinya jauh lebih banyak dan bisa lebih powerful. Jadi kira-kira begitu.
**Mardhani - Biro Transdig UGM** (88:04): Nah, contoh juga tadi yang tempatnya Pak Varta, ya, yang terkait disaster itu pakai kita pakai Sahabat AI, ya. Jadi, dengan timnya Indosat, saya sebut Achenji, itu kan kita juga
**Mardhani - Biro Transdig UGM** (88:16): Sebelumnya, kerjasama Pak membangun data model untuk bahasa Indonesia sendiri namanya Sahabat AI, kalau itu?
**Mardhani - Biro Transdig UGM** (88:23): Dan pengalaman kami itu jauh lebih powerful dibanding model tadi yang disebutkan.
**Mardhani - Biro Transdig UGM** (88:30): Karena itu, lekobis jadi dia secara konteks mengenali.
**Mardhani - Biro Transdig UGM** (88:35): Informasi yang berbahasa Indonesia tuh bahasannya enak-enak konteks ya. Kalau kita terjemahan itu kan nak grammatical-nya gitu, dia gramatikalnya, tapi kalau ini konteksnya jadi semacam.
**Mardhani - Biro Transdig UGM** (88:58): Satu yang bisa dibahas kalau kami, ya, kalaupun dijujur merekomendasikan, mungkin memang sudah saatnya, ya, kita mendengkakeyang data model yang memang sudah
**Mardhani - Biro Transdig UGM** (89:07): Sangat sangat sesuai dengan konteks kita di Indonesia, begitu. Nah, ini yang sedang kami dorong sehingga nanti mungkin kami sedang memikirkan, mungkin tidak perlu ada Sahabat AI kan, Indosat ini ada Sahabatu GM bukannya?
**Mardhani - Biro Transdig UGM** (89:21): Gini ya, tapi Indonesia gitu, ya. Jadi, itu yang kita dorong nanti berkontribusi menjadi satu-satu dictionary. Itu akan sangat baik sekali, cuma ini harus ada yang memulai, Pak. Ini yang kami
**Mardhani - Biro Transdig UGM** (89:33): Mentemen di IPP juga udah punya khususnya sendiri itu dengan apa tuh namanya?
**Mardhani - Biro Transdig UGM** (89:40): Bu Ayu itu NLP-nya apa namanya? Tuh lupa saya bahasa apaan gituin semacam itu. Dia memang sudah punya masing-masing kan, keman tuh Pak ya kalau silo-silo juga. Nah kira-kira begitu. Begitulah Pak, jadi.
**Mardhani - Biro Transdig UGM** (89:51): Jadi kalau nanti masalah open apa tidaknya, sebenarnya kalau secara teknis sih itu open aja karena library-nya ada di mana, tapi tadi yang masalah tune up dan tuning-nya, tadi yang fitting ya, tuh yang nantinya.
**Mardhani - Biro Transdig UGM** (90:03): Perlu kita lihat, ya, saya kira begitu.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (90:21): Artinya sama, artinya sama pun cara menyajikannya beda dan pikirnya berbeda. Modelnya beda. Kemarin itu kami seperti biasa, tahun ini ketemu DPR, bera gitu. Salah satu anggota DPR-nya ada Pak.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (90:48): Ideal bahwa itu berdampak terhadap sasaran target pembangunan. Kan mungkin ini seperti ini ya, sebenarnya Pak Karo tadi sampaikan sama seperti rekan kami yang di Direktorat Produktivitas. Beliau sama direkturnya diminta mengukur jangan pemerintah nih meningkatkan produksi.
**Mardhani - Biro Transdig UGM** (91:03): Pingkatan sebenar kalau mengukurnya by number mungkin susah, tapi nah seperti ini. Mungkin Pak Kal itu ya sama seperti misalnya kayak kegiatan ini, Pak. Jadi kalo kami di dalam POV kami, ya kamu menerima beberapa nasihat. Nanti kalau ini kami bikin berita, itu segera, bukan hanya untuk
**Mardhani - Biro Transdig UGM** (91:19): Untuk menambah berita di website, tapi sebenarnya itu dokumentasi yang nanti akan memfitting ke mesin AI kali, sehingga ketika ditanya, Nantinya UGM itu dampak ke mana ya, siapa tahu apa muncul di situ nanti. Mesinnya belajar, "Oh, pernah nih bantu Bappenas."
**Mardhani - Biro Transdig UGM** (91:35): Pangkat di benchmark gitu ya? Jadi kayak itu, Pak. Nah, itu akan sangat mudah, gitu loh pastinya.
**Pak Ewin - Sesdep PMP** (91:41): Ya apa ya, Pak? Ini saya bagi saya sendiri dan saya harap juga teman-teman saya ini yang datang nih, soalnya kan ini membuka pikiran ya, Pak. Kita benchmarking itu kan jangan ke
**Pak Ewin - Sesdep PMP** (91:52): Kita cuma baca, coba ngunik-ngunik sendiri di kantor. Itu saya selalu bilang gitu, "Pak, kita coba buka." Dan semakin tadi disampaikan terakhir oleh Pak Karo, tuh, saya kira jelas sekali bahwa semuanya itu dicobak bagaimana?
**Pak Ewin - Sesdep PMP** (92:02): Bagaimana menyambungkan gitu, Pak? Menyambungkan sehingga semuanya menjadi data source atau menjadi pantauan lah ya, Bet, Pak. Jadikan pantauan untuk memfeeding si mesinnya gitulah, Pa. Nah, ini yang saya kira apa namanya, ini juga mulai pikirkan nih, Mas Adek.
**Pak Ewin - Sesdep PMP** (92:17): Jadi karena ini banyak sekali, Pak, mau data anggaran, datanya apa, tinggal nanti mungkin kita harus memilih. Tadi Bapak sampaikan ada yang dia ciphernya jangan keluar dulu. Walaupun saya juga ini masih ragu-ragu, Pak, yang dibikin oleh Mas Adit ini, apakah benar sih? Nggak, si Gk Keluhkan?
**Pak Ewin - Sesdep PMP** (92:32): Nanti karena emang seperti itu, tapi saya harapkan karena ini kan source-nya dari di dalam, Pak, disimpan di baru. Simpelnya di mana sih drive-nya? Dia apa? Drive diskervoin, lah, diskervoinya yang kita tidak ngambil source luar dulu, Pak, gitu kira-kiranya.
**Pak Ewin - Sesdep PMP** (92:47): Mau mesin tesakan loli yang ada di dalam, tapi yang perlu dipikirkan sebenarnya bener, Pak, ini ketika bikin konten pun gitu, bukin ini pon itu sebanyak nanti harusnya masuk untuk memfeeding si sjen gituyah? Ini yang.
**Pak Ewin - Sesdep PMP** (93:02): Saya kira apa namanya?
**Pak Ewin - Sesdep PMP** (93:05): Pemikiran-pemikiran seperti ini, Pak, yang teman-teman saya kira seharusnya juga mampu menyerap. Dan yang paling pentingnya, kami sepakat, Pak, dengan Bapak tadi, apa learning by example, gitu lah kalau saya bilang ke teman-teman, tuh harus ada barangsih.
**Pak Ewin - Sesdep PMP** (93:17): Jadi, jangan nomor-nomor dulu. Pokoknya barangnya di ada, itu mau sesimple apa kita nanti?
**Pak Ewin - Sesdep PMP** (93:24): Tumbuh belajar dari barang yang sederhana itu, saya kira ini kan penekanan nih ke teman-temannya Pak. Ini ya udah lah, pokoknya ada dulu barangnya. Ada simple dulu, belajar.
**Pak Ewin - Sesdep PMP** (93:34): Nanti dengan cara apa pun kita coba kembangkan. Tadi Bapak sampaikan baby step, atau kalau enggak, ya model-model yang ada di luar dikulik, diadopsi, diterivers gitu, ya, Pak. Bisa nggak sih kita ambil? Ini saya karena nih saya luar.
**Pak Ewin - Sesdep PMP** (93:47): Biasa, Pak Mardhani. Ini terima kasih banyak, Pak. Nanti sebelum mungkin tim yang lebih detail, tapi ini bagi saya, nih. Saya pakai kesempatannya juga untuk mengingatkan saya sendiri dan teman-teman, Pak. Ini bahwa ini mungkin harus sering-sering, enggak malah?
**Pak Ewin - Sesdep PMP** (93:59): Ini kita benchmarking, tapi harus ada tindak lanjut sama outputnya ya, Pak, sekiranya walaupun sederhana. Ini saya harapkan nanti mungkin ada beberapa hal dari yang ditampilkan oleh Pak.
**Pak Ewin - Sesdep PMP** (94:11): Mardhani dan tim ini juga nanti ya kita bisa coba adopsi, entah dari pola apa namanya ekosistemnya, Pak. Mungkin kalau saya membayangkan balik ke sini, saya punya gambaran tadi teman-temannya ekosistemnya UGM ini ketika membangun ini.
**Pak Ewin - Sesdep PMP** (94:22): Apa ini ada cabangnya di sini? Ada cabang niara pondasinya di sini gitu ya, Pak, sehingga ini bisa jadi gambaran kita untuk diskusi dengan teman-temannya Pusdatin, Pak, karena ini bukannya dengan infrastruktur digital yang mungkin, bukankah kami yang menyediakan itu nanti.
**Mardhani - Biro Transdig UGM** (94:46): Sedikit menunjukkan nih, Pak, ini tadi dampak, mungkin bisa salah satu yang detail, Mas, terutama lebih lingkungan. Ini misalnya?
**Mardhani - Biro Transdig UGM** (94:57): Atah ekonomu?
**Mardhani - Biro Transdig UGM** (95:03): Usrol ke bawah. Nah, jadi ini nanti Bapak Ibu bisa lihat ya. Jadi yang menarik lagi begini, Bapak Ibu, jadi kalau nggak support by angka tadi itu kan ya biasanya hanya menampil
**Mardhani - Biro Transdig UGM** (95:16): Kan etalase gitu ya. Nah, kalau di sini bedanya, Bapak, Ibu, kita ingin mendorong itu bahwa
**Mardhani - Biro Transdig UGM** (95:22): Ketika kita membaca data itu.
**Mardhani - Biro Transdig UGM** (95:24): Bahasa kasar saya itu ada ceritanya, jadi kalau bahasa di data science itu ada teknik, Bapak, Ibu, menyajikan visualisasi itu harus tell all story.
**Mardhani - Biro Transdig UGM** (95:33): Jadi, kita harus membayangkan bahwa pengguna itu ya belum dapat insight apapun, sehingga kita harus teruskan kira-kiranya begitu. Nah, ini yang kita coba lakukan. Jadi, contohnya yang pertama, kita ada
**Mardhani - Biro Transdig UGM** (95:46): Ringkasan dan insight itu untuk membuka bahwa, oh ya, ini tentang analisisnya yang terengah-engahan. Skop-nya tentang apa? Terdiri dari apa saja? Kalau bahasa teknis, mungkin ada eksploratori data analytic dulu, ya.
**Mardhani - Biro Transdig UGM** (95:58): Statistik FIS, terus kemudian nanti kita masukkan, misalnya, oh ya, pertama adalah bahwa peta tema.
**Mardhani - Biro Transdig UGM** (96:05): Berdampak ini berdasarkan kriteria apa? Nah, kadang kita tidak menjelaskan tribut yang harus dianalisis, gitu ya.
**Mardhani - Biro Transdig UGM** (96:16): Tiba-tiba pokoknya muncul sentimennya positif gitu. Nah, sensus itu kenapa? Apakah emotikon yang kos-yang smiley atau kata-kata yang pas gip baik aja?
**Mardhani - Biro Transdig UGM** (96:28): Jadi semacam itu. Nah, ini yang kami coba lakukan juga. Harapannya gini, Pak, nanti di ujung ketika membaca kesimpulan.
**Mardhani - Biro Transdig UGM** (96:34): Pembaca dan kita tuh satu frame.
**Mardhani - Biro Transdig UGM** (96:37): Gini ya, jadi itu. Jadi gitu, jadi tidak.
**Mardhani - Biro Transdig UGM** (96:42): Jangan kita lihat ya, kadang-kadang itu terus cuma dikrop?
**Mardhani - Biro Transdig UGM** (96:45): Social media dikasi caption aneh-aneh terus irawal kan gitu, jadi sebenarnya kita ada ini juga untuk mengedukasi kita bahwa kalau kita mengek... Kalau ini mungkin kami terlalu jauh ya, tapi kalau kita mengimplementasikan Undang-Undang
**Mardhani - Biro Transdig UGM** (97:09): Miliknya lagi gitu, jadi kita harus berhati-hati di situ, sehingga ini semacam statement of disclaimer bahwa konteks kita menyajikan data itu seperti ini. Nah, kira-kira begitu. Jadi kalau ada pertanyaan kayak gini, kalau ada pertama yang
**Mardhani - Biro Transdig UGM** (97:21): Itu konteks gini, itu di luar konteks, tapi itu ide bagus. Nanti bisa kita masukkan sebagai analisis berikutnya. Jadi kira-kira semacam itu. Nah, ini yang menarik, Bapak, Ibu. Jadi kita munculkan dan
**Mardhani - Biro Transdig UGM** (97:34): Dan ini yang menarik, teknik-teknik kita menyajikkannya juga kalau bisa ya, karena kami ya lebih cenderung ke berbasis ilmiah, yaitu kita cobalah basis ilmiah kemudian.
**Mardhani - Biro Transdig UGM** (97:45): Nanti pemilihan visualisasi juga harus clear gitu ya, dan kemudian nanti macam-macam. Dan kemudian ada kebutuhan juga si user ini bisa secara flat.
**Mardhani - Biro Transdig UGM** (97:57): Tabel memilih tema, misalnya?
**Mardhani - Biro Transdig UGM** (97:59): Jadi nggak, kan model yang kita bangun itu tuh kan tidak-tidak, modalnya malah kebalik, Pak. Bukan agregasi, tapi detailing. Nah, ini yang strategi analisis yang coba kita bangun gitu, Pak. Tapi ini kembali lagi ke desain ya, ketemu.
**Mardhani - Biro Transdig UGM** (98:15): Desain dari awal di semacam itu. Nah, ini semacam itu, terus kemudian jadi semua ya semacam ini, kadang bahkan ada yang selip.
**Mardhani - Biro Transdig UGM** (98:27): Kata-kata yang memang adanya tidak terlalu clear maksudnya apa ya, muncul-munculin aja kadang karena atas dasar ada nih, maaf teman-teman yang basic statistiknya sangat
**Mardhani - Biro Transdig UGM** (98:39): Kuat ya, tapi dat layer itu malah dihilangkan atas dasar ilmu statistik. Kalau kami malah kebalik, Pak. Malah kami pelihara, Pak.
**Mardhani - Biro Transdig UGM** (98:47): Karena itu, yang memberikan informasi, ada informasi yang meskipun kita sudah anggap tuh single source of data sudah benar dari instansi yang benar, tapi juga ada yang anomali.
**Mardhani - Biro Transdig UGM** (98:59): Nah, kira-kira begitu kalau bahasa kami, karena kebetulan saya juga basically atau fonting ya, itu, yeah, cerca pun anomali itu untuk masuk vok, Pak. Oh, gitu. Jadi kira-kira gitulah, ini yang menjadi maksudnya dalam konteks siang.
**Mardhani - Biro Transdig UGM** (99:13): Ya, tapi intinya semacam itu. Jadi, ini kita ingin melihat semacam itu, sehingga ketika itu bisa kita lakukan, ya, akan sangat menarik. Nah, ini contoh nih model, kalau bahasa teknisnya tuh ini konsepnya tuh teknik drone analytic, jadi.
**Mardhani - Biro Transdig UGM** (99:28): Makin-makin macam ke bawah, kira-kira begitu. Nah, ini yang kita kerjakan semacam itu. Nah, ini untuk nanti berlaku juga untuk masing-masing tema. Dan ini generitid atau Generitet ya untuk
**Mardhani - Biro Transdig UGM** (99:43): Wordingnya nanti bisa tren musiman, kemudian bisa macam-macam, jadi bisa kita lihat nanti. Tergantung Mbak Pebu, misalnyanya untuk keperluan presentasi, kami mendorong sih kalau ini. Lagi, saya sedang mentraining direktur, Bu, kalau representasi nggak usah pakai portfolio.
**Mardhani - Biro Transdig UGM** (99:58): Luk, gimana? Survive kayak gitu-gitu, jadi itu impresif. Kita kembali terpofil, Pak.
**Mardhani - Biro Transdig UGM** (100:07): Lagi di Jakarta itu. Oh iya, Iya, berarti apa namanya kalau bahasa sistem tuh ada tooltips, Pak? Isinya ya.
**Mardhani - Biro Transdig UGM** (100:18): Kilat-kilat yang mau kalau pimpinan pacar pastu ngerti ya maksudnya ini yah gitulah itu atau kalo seluar kan ada ke Arcana.
**Mardhani - Biro Transdig UGM** (100:28): Itu pernahnya cuma menghindari itu di waktu karena selalu bikin gitu, sering bikin tuh amat dan
**Mardhani - Biro Transdig UGM** (100:35): Iya nih, mohon maaf, ini nanti Bapak juga akan disup pakai gitu ya, jelas.
**Mardhani - Biro Transdig UGM** (100:43): Ini kan? Ini kayaknya deh.
**Mardhani - Biro Transdig UGM** (100:57): Sumber berita bisa mendukung dua impact, loh, Pak Yunus menangkap poinnya. Jadi, ini menarik, Bapak, Ibu. Jadi, kan kita merasa satu hasil analisis itu harus disupport oleh satu sumber.
**Mardhani - Biro Transdig UGM** (101:09): Kami punya banyak sumber padahal.
**Mardhani - Biro Transdig UGM** (101:12): Nggak begitu kalau dalam dunia. Kalau kebetulan ini begini, Pak, ini mungkin sedikit rahasianya. Cara berpikir kami adalah di belakang AI itu, AInya kita seperti ini, tuh tidak akan. Mungkin ada.
**Mardhani - Biro Transdig UGM** (101:23): Tanpa big datanya, nah, kita harus paham juga nih, Mbak. Ini yang mungkin kita kadang, kalau bahasa saya ketinggalan ya, ini sudah melompat, Pak A draftnya? Kita itu malahan generik, banyak data lagi.
**Mardhani - Biro Transdig UGM** (101:35): Nah, akhirnya kan mungkin tadi seratus pasien bisa versinya kan banyak banget. Saya yakin pada titik-titiknya tuh bingung, ini versi terakhir yang paling benar mana nih? Nah, kita begitu. Nah, ini jadi masalah sehingga kita mendorong sebenarnya kalau kita sudah mempercayai
**Mardhani - Biro Transdig UGM** (101:50): Yay, satu data ini udah yang kita preserve jadi data primary dan menjadi acuan untuk.
**Mardhani - Biro Transdig UGM** (101:58): Pendekatan yang lain, tapi ketika muncul, "Pak, datanya ini valid, makainya tadi, Pak, kami larinya melalui proses bisnis, memastikan yang mengambil ke sini benar."
**Mardhani - Biro Transdig UGM** (102:09): Itu, itu yang poinnya di situ sebenarnya. Nah, ini yang kami di belakang itu sebetulnya ada usaha untuk menyusun kata, tidak harus punya survei besar, tapi kalau Samy nyebutnya di situ.
**Mardhani - Biro Transdig UGM** (102:20): Putih data, jadi saya percayakan data tentang berita ini ada di humas. Makanya saya kencuin ke humas biar tahu caranya data-data tentang
**Mardhani - Biro Transdig UGM** (102:44): Karena kami sadar, Pak, kalau di UGM itu untuk dijadikan satu itu sulit, Pak. Kita sama kayak Indonesia, Bang, mulawulang, jadi gitu, ya. Jadi, ya sudahlah, nggak apa-apa, yang penting ada bini kantung galikanya.
**Mardhani - Biro Transdig UGM** (102:56): Apa Pak Mas Hendy Unika tunggal pilih terhadap karena itu tetap mengerti ini kami pakai juga. Kami yang ambil tuh jadi semacam itu, tapi dari
**Mardhani - Biro Transdig UGM** (103:08): Besar itu, Pak? Itu ternyata mendorong kami juga akhirnya efeknya mentransformasi cara proses bisnis yang ini, artinya tadi usaha bukan.
**Mardhani - Biro Transdig UGM** (103:16): Proses bisnis itu diubah, benar, tapi terintegrasi.
**Mardhani - Biro Transdig UGM** (103:20): Itu jadi intinya di situ memang idealnya kalau kita mau rapi ya seperti company itu bagai enterprise system gitu ya, tapi kan ya kita nggak punya kekuatan sebesar itu.
**Mardhani - Biro Transdig UGM** (103:32): Berarti biro Bapak mewajibkan semua unit kerjanya untuk mengalirkan data itu atau sebenarnya tidak korelasi? Kami tidak mewajibkan karena kami Biro Litbang, bukannya seperti biro di kementerian, ya?
**Mardhani - Biro Transdig UGM** (103:44): Biro itu untuk biro tuh seperti?
**Mardhani - Biro Transdig UGM** (103:46): ngapain ya?
**Mardhani - Biro Transdig UGM** (103:49): Hah? Apaan, Mas? Apaan, Pak? Kami itu di sisi brand-nya mereka. Jadi, kami malam melakukannya itu di sisi non-normal, Pak. Menurut saya.
**Mardhani - Biro Transdig UGM** (104:01): Apa sih? Jadi apa gak bisa selesaikan di bukan, Pak Di, sambil ngopi lah ya, bahasa kami gitu. Sambil nongkrong. Jadi lebih banyak ke situ. Nah, ini juga, Pak, ini salah satu bentuknya. Kalau biasanya kan
**Mardhani - Biro Transdig UGM** (104:13): Data KPI capaian universitas kan publikasi beberapa kali lebih. Nah, itu juga move sekarang, Mbak, tidak lagi number of something, tapi
**Mardhani - Biro Transdig UGM** (104:25): Ada analisisnya. Nah, contohnya seperti ini. Ini diinisiasi oleh teman-teman di Teknik Mesin. Mereka mengambil data ini. Menarik, Pak, datanya?
**Mardhani - Biro Transdig UGM** (104:36): Ini kami punya masalah, Pak, dengan mohon maaf ya, Pusdatin-nya dengan kami Pustating. Kami itu karena merasa dirinya itu harus menjaga data dengan sungguh-sungguh dan benar-benar serius, tidak boleh keluar sedikit pun.
**Mardhani - Biro Transdig UGM** (104:49): Sampai kami minta data pun tidak dikasih? Oh, gitu, Pak. Jadi itu, nah, pasti ada sentimen kayak begitu juga. Teman-teman berdatanya online, kan, gitu, kan? Tapi ini karena Pak Kami.
**Mardhani - Biro Transdig UGM** (105:01): Kami rel respek gitu, berarti prinsipnya strong. Meskipun dari sisi saya komputer saint gemes juga ini, tapi usahanya gimana? Oh ya, cara ini, ini bedannya biro, Pak, kalau kami biro.
**Mardhani - Biro Transdig UGM** (105:13): Ini agak birunya itu, mohon maaf nih, agar-agar sedikit.
**Mardhani - Biro Transdig UGM** (105:18): Ompe, kalau bahasa kami itu sampai diculukin, wah, ini partner incline nih, jadi suka-suka bikin anu, Pak, nabrak-nabrakan gitu. Akhirnya yang kami lakukan adalah calling data dari sumber luar, Pak, yang memang readable dalam hari ini, misal aplikasi.
**Mardhani - Biro Transdig UGM** (105:31): Itu dari Scopus, ini pun juga nggak bisa rolling-nya itu langsung. Nanti kan harus spend pelan-pelan. Nah, kita untuk ikutin rule of the game ya mereka, tapi data kita ambil.
**Mardhani - Biro Transdig UGM** (105:43): Kita usahake gitu, Pak. Nah, akhirnya terjadi kita bisa mendisplaykan.
**Mardhani - Biro Transdig UGM** (105:49): Lebih lebih tajam daripada sekedar number of data. Tadi number apa dalam angka tadi? Contohnya seperti ini, Pak. Ini, Pak, kalau tadi kita nyebutnya kan tidak?
**Mardhani - Biro Transdig UGM** (106:01): Satu-satu departemen perproksi yang paling disitasi itu bisa kita tampilkan. Kalau kata Ma, depan saya sih itu kita mining di sistematis sendiri aja bisa, tapi.
**Mardhani - Biro Transdig UGM** (106:23): Nah, tadi ini salah satu bentuk working example, Pak. Itu menunjukkan begini, nggak kemarin saya sampaikan kalau kita mengambil data? Kalau kita ambil data dari luar, bisa kayak gini loh, padahal datanya ada di dalam. Nah, sekarang.
**Mardhani - Biro Transdig UGM** (106:36): Saya mintak sehingga saya tanda kutip, maaf ya, Saya bisa mereta direktor Pak, Ibu yang harus sekarang minta begitu keuntungan Bu, gitu. Ya. Oh iya, itu gunanya rektor sudah dimarahin?
**Mardhani - Biro Transdig UGM** (106:48): Oh, jadi ngajain saya gitu? Nah, itu biasanya mau jawaban Ibu ini semacam tuh, bukan macam itu, Pak. Nah, ini bisa kita lihat, Pak, masih misalnya ya, orang seperti apa posisinya di mana.
**Mardhani - Biro Transdig UGM** (107:00): Kami bayangin nggak ya, Bapak, Ibu, tadi? Ya pakai bukan punya hasil kajian pasti, satu kajian itu ada timnya.
**Mardhani - Biro Transdig UGM** (107:07): Efeknya berlantai, Pak, bisa untuk API SPM. Pastinya nanti bisa juga sampai waktu yang sampaikan tadi. Kalau di sini kita bisa lihat, misalnya Mas Alif yang tadi, yang peta.
**Mardhani - Biro Transdig UGM** (107:17): Peta ini author pasti Bapak Ibu, sebabnya juga sudah punya ya buat dokumen? Ini kita bisa lihat hubungkan satu sama lain. Jangan-jangan Pak Yunus ini bikin kajian CSIRT-nya cuma Pak begitu hadir terus gitu. Hanuh harus hanuk dipecah lah.
**Mardhani - Biro Transdig UGM** (107:32): Nanti nggak baik, Pak, kalau misalnya kita loh misangin, engga ilmu sisa gitu ya. Mungkin dasar kalau kami untuk melihat niat balance, Pak, antara dosen senior dengan dosen juniornya tuh tujuannya bukan apa-apa, Pak, tapi berilmunya itu.
**Mardhani - Biro Transdig UGM** (107:47): Lang-lasting gitu loh, Pak, karena kita udah mulai yang dapat tuh begitu seniornya sudah pensiun atau tiba-tiba beberapa tahun kemarin ada kejadian, terus masih produktif tapi sudah harus kesawit sari, itu kan kehilangan ilmu. Nggak ada yang istilmiah?
**Mardhani - Biro Transdig UGM** (108:03): Nah, ini kita identifikasi dari sini bahwa ternyata ada bidang-bidang ilmu yang mengkhawatirkan nih.
**Mardhani - Biro Transdig UGM** (108:09): Mungkin kita tahu?
**Mardhani - Biro Transdig UGM** (108:11): Kemudian ada terutnya siapa saja? Terus kemudian muncul gap-nya juga, Pak. Kajian-kajian itu jangan-jangan ada silonya juga, nggak tersambung, nggak terhubung. Nah, juga bisa jadi, Pak Bappenas, nanti hasilnya dari di departemen yang berbaik ini mengganggu.
**Mardhani - Biro Transdig UGM** (108:27): Apartemen yang lain karena merasa, "Oh iya, ternyata saya selama ini kacau juga nih," misalnya kayak gitu. Nah, itu yang harus kita lakukan. Nah, ini bisa kita buat, Pak, sehingga?
**Mardhani - Biro Transdig UGM** (108:35): Ini mungkin lesson-lessonnya, satu guided boarding-nya Tenda Kutik itu tidak satupun sport everything on there, Pak, tapi spesifik.
**Mardhani - Biro Transdig UGM** (108:46): Agar terjedet Pak, karena kalau tadi kayak dalam angka yang umum tadi.
**Mardhani - Biro Transdig UGM** (108:51): Jadinya hanya pacangan, Pak. Makanya, Bapak, Ibu, kalau tanyakan ke kami, "Pak UGM punya ruangan gasport khusus nggak?" Itu mengolah, kami hindari, ya?
**Mardhani - Biro Transdig UGM** (109:00): itu.
**Mardhani - Biro Transdig UGM** (109:01): Itu hanya untuk eksperimental, oke gitu ya, tapi.
**Mardhani - Biro Transdig UGM** (109:04): Spesifik-spesifik ini dan ini kita display di masing-masing spesifik direktorat, jadi senjata mereka. Nah, kira-kira gitu ya. Khusus proyek tuh kami asilinnya lengkap di depan, tapi biasanya nggak sempet juga. Ya, karena kalau ada kasus khusus, biasanya baru bila
**Mardhani - Biro Transdig UGM** (109:20): Lihat, nah, ini kita juga melihat persaingan kita tuh seberapa jauh dengan yang lain, itu bisa. Dan ini datanya satu, Pak, datanya satu, model analisisnya bisa beragam. Nah, jadi ini yang
**Mardhani - Biro Transdig UGM** (109:32): Poin yang mungkin salah satu strategi juga untuk mengembangkan dan support depan, kira-kira begitu?
**Mardhani - Biro Transdig UGM** (109:41): Kemudian kalau yang anunya Mas Ali mungkin ya riset enterprise-nya?
**Mardhani - Biro Transdig UGM** (109:46): Kita lihat, nah, ini, Pak?
**Mardhani - Biro Transdig UGM** (109:48): Ini salah satu efeknya begitu kita punya macam-macam sudah seperti itu, kita jadi mulai ada kesadaran, Pak U, ya? Ternyata sistem kita yang silo masing-masing itu yang menyebabkan kadang kita nggak bisa menghasilkan data analitik.
**Mardhani - Biro Transdig UGM** (110:04): Atau dashboard yang lengkap sehingga ada kebutuhan, Mbak, ini akhirnya.
**Mardhani - Biro Transdig UGM** (110:09): Ini sudah mulai jalan sejak tengah tahun ini. Kita udah piloting untuk.
**Mardhani - Biro Transdig UGM** (110:14): Mengintegrasikan semua ekosistem pembuatan, kalau kami penelitian, ya mungkin Bapak-Bapak kajian itu dari ide Pak?
**Mardhani - Biro Transdig UGM** (110:22): Jadi yang diadministrasi atau direkam sistem itu prosesnya, hasil akhirnya. Jadi dari ide, bikin timnya, bukan proposalnya, log.
**Mardhani - Biro Transdig UGM** (110:33): Pengembangannya sampai nanti hasil akhir itu semua ada di situ, nah sehingga ini jadi breakthrough juga untuk kita mengubah.
**Mardhani - Biro Transdig UGM** (110:41): Macam-macam dari awal, dari awal nanti ini efek-efek saya dulu mikirnya meneling dulu sistemnya, baru-baru datanya, kan baik. Tapi di sini ternyata malah dibalik karena ada AI, ya?
**Mardhani - Biro Transdig UGM** (110:53): Kita tunjuknya itu selalu menunjukkan gap-gapnya kebutuhan ke sana tuh jadi lebih sulit.
**Mardhani - Biro Transdig UGM** (110:58): Kira-kilo jadi sebenarnya dulu awalnya ketika saya pertama kali di Rio ini yang saya bawa Pak, enam bulan pertama tivil mengaku itu nang Bulan Pertama Saya promosi, nggak ada yang mau lah.
**Mardhani - Biro Transdig UGM** (111:09): Karena belum merasa ada kebutuhannya, jadi terlalu cepat.
**Mardhani - Biro Transdig UGM** (111:13): Nah, saya pending dulu. Nanti strategi, oke, kita mainin datanya dulu. Obrol abri datanya, orang merasa bahwa ada kepentingan, itu penting. Nah, terus ada pertanyaan, lo gimana biar bisa? Sih, benar caranya gini. Nah, kira-kira begitu lah gitu kan?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (111:30): Wah! Ini itu?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (111:33): Kalau jadi kita bicara dari mulai apa, nama menyusun database yang baik, kurasinya sampai ujungnya masuk ke impact, Pak Ses. Jadi yang Bapak sampaikan benchmarking-nya kita.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (111:45): Selain lihat yang apa? Yang kita mulai inisiasi UGM kan memang lebih bagus, Pak, tapi ternyata Beyond itu kita dapat tambahan, ya, harus bikin juga untuk yang impact, karena mungkin ke depannya akan ada lagi peluang lain di bidang ini, terutama dalam hal pembiayaannya dan kemudahannya, sehingga bisa dilakukan oleh perusahaan-perusahaan.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (111:57): Memang seperti yang saya sampaikan, Pak Karo, banyak sekali pertanyaan dari stakeholder gitu, dengan anggaran kementeriannya sebesar ini, terus kebijakan yang disusun tampaknya itu apa? Nah, itu sepertinya cara.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (112:09): Menjawab sekarang itu belum bisa memuaskan lah stakeholder. Gitupun belum bisa memuaskan karena mungkin juga tidak disajikan secara terstruktur ya, besar struktur. Jadi mungkin ini mengenai?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (112:21): Arah depan juga mungkin Pak Sas jadi banyak usulan output dari direktorat di bawah Pases dan kita tidak punya mekanisme untuk memfilter seperti itu, katakanlah kalau tadi.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (112:33): Pak Aru bisa melihat ternyata sekelasmah ini kajian-kajian logistik kayaknya mendominasi, memang excellencenya, sentral excellence-nya memang di situ ya. Mungkin kita mungkin bisa lihat juga, Pak.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (112:45): Sesensi nanti usulan output dari direktorat itu memang dia penting dan perlu untuk dijalankan di tahun depan atau enggak gitu? Jangan-jangan kita lagi nggak butuh itu? Jangan, Pak Deputi, apa Menteri butuh output yang lain.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (112:57): Yang lebih dibutuhkan gitu, Pak. Saya rasa mungkin kita coba untuk situ juga, Pak. Ses nanti baik, mungkin Bapak dan Ibu ini juga.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (113:21): Pemanfaatan pembelajaran, pengembangan, serta pemanfaatan dashboard di UGM. Temen-temen juga tadi sudah ada beberapa pertanyaan. Ini nanti yang perlu kita ketahui, mungkin?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (113:31): Untuk buat nextnya nih, nah untuk next saya ini, saya mungkin harus minta arahan dari Pak Ases. Dan ini kira-kira Pak Ases pengen berkenan kita WhatsApp-nya dengan.
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (113:43): Pak Caro gitu akan seperti apa, Pak? Mohon izin perkenan arahan dan sekaligus itu menutup sesi di pagi ini, Bapak. Makronun mak.
**Pak Ewin - Sesdep PMP** (113:55): Pak Karo dan tim ini?
**Pak Ewin - Sesdep PMP** (113:59): Sekali lagi, saya ucapkan terima kasih. Luar biasa sekali, Pak, ini membuka kawasan, apa namanya, jangkrawala berpikir utama bagi saya, gitu ya, Pak?
**Pak Yunus - Plt Kabag PMRU Sesdep PMP** (114:11): ahh.
**Pak Ewin - Sesdep PMP** (114:13): Banyak hal-hal bagus, Pak, ini yang kita bisa adopsi, gitu ya, Pak? Yang paling mendasar dari sisi ini, Pak.
**Pak Ewin - Sesdep PMP** (114:36): Ini untuk analisis rencana-rencana output direktorat. Juga mungkin bisa juga ini kita seperti ini, gitu ya. Kemudian dampak itu tadi, Pak. Kalau kemudian saya sendiri yang sih?
**Pak Ewin - Sesdep PMP** (114:48): Simpel, Pak. Ini kan naskah dinas dari setiap direktorat tuh tiap hari, Pak, melaporkan kepada deputi berbagai macam hal. Sedikit tidaknya kalau saya masukkan seluruh analitikal, sebenarnya di area mana yang?
**Pak Ewin - Sesdep PMP** (115:00): Hevy, gitu ya, jangan-jangan ada area tertentu yang kelihatannya galau dibandingkan dengan areanya. Ini itu sudah memberikan informasi luar biasa sekali kepada para deputi, gitu ya?
**Pak Ewin - Sesdep PMP** (115:11): Menu yang saya pikir ini kita perlu tindak lanjuti, Pak. Kami mohon izin nanti, Pak, nanti sekiranya kami menghubungi kembali atau nanti berkesempatan nanti mungkin.
**Pak Ewin - Sesdep PMP** (115:23): Lain kali Pak Madani yang datang ke kantor Pak, walaupun ini kan online semua administrasi lagi itu, tapi mungkin diskusi di Jakarta, saya berharap sih sebenarnya.
**Pak Ewin - Sesdep PMP** (115:34): Karena tadi Pak, apa yang sifatnya mungkin level kebijakan di kementeriannya, misalnya berdampak tadi ya. Walaupun kalau misalnya belum yang apa, Pak, saya, saya tuh senang menjadi bikin contoh aja. Ba, mulai dari
**Pak Ewin - Sesdep PMP** (115:47): Sederhana-sederhana kita mulai nanti, mungkin karena tadi saya pikir orang tuh kan ini Tani kasih contoh, belum melihat hasilnya, belum ngeliat dampaknya, tidak bermanfaat buat mereka itu.
**Pak Ewin - Sesdep PMP** (116:11): Sudah, sudah sempat ditunjukkan. Nanti ya, sudah sempat ditunjukkan tadi. Mungkin di lain kesempatan, Pak, mungkin dengan kami ngasi itu. Nanti mungkin, mohon izin, Pak, kalau berkenan, nanti ada spesifik masuk mengenai apa yang ada di kami gitu, Pak, baik dari sisi
**Pak Ewin - Sesdep PMP** (116:26): eh?
**Pak Ewin - Sesdep PMP** (116:27): In general, apa platformnya sudah cukup benar? Apakah enggak gitu, Pak? Efisiensi bekerjanya kan kadang kita bisa bikin terlihat mungkin ngga efisien, Pak. Ngga efisien.
**Pak Ewin - Sesdep PMP** (116:37): Ini ada jolimit, lah. Mungkin ke sana dulu, baru ke sini. Bener, harusnya bisa loncat gitu ya, Pak? Atau ini salah mesinnya? Tuh, bukan mesinnya yang efisien nih. Gitulah, Pak. Ada langkah-langkah yang nggak penting itu. Ya, baik, Tikit.
**Pak Ewin - Sesdep PMP** (116:48): Tiket pagal gini dikira nggak kurus juga gitu kan, Pak? Mungkin itu yang kami juga mohon izin masukkan, Pak, berdasarkan mungkin pengalaman Bapak tentunya dan ini apa namanya, ya?
**Pak Ewin - Sesdep PMP** (116:59): Bagusnya kalau sudah memulai tuh mengetahui lebih sering diminta lagi informasi sehingga tahu kayak ini bicara hal ni mas. Ini kamu?
**Mardhani - Biro Transdig UGM** (117:10): Ini nanti kan kalau mereka akan masalah ini kayaknya pelan-pelan dulu gitu, karena ini mungkin.
**Pak Ewin - Sesdep PMP** (117:27): Kolaborasi, Pak, kolaborasi yang
**Pak Ewin - Sesdep PMP** (117:30): Sebelum orang ditanya, Pak, tapi hari lihat Bapak itu, mungkin kita bisa temukan bersama, misalnya masalah dampak tadi Bapak sampaikan, ya. Masalah dampak, kemudian apa namanya, maknanyakan, misalnya ada produknya dari teman-teman.
**Pak Ewin - Sesdep PMP** (117:45): Teman di Fakultas Ekonomika dan Bisnis, misalnya, ya, Pak, yang spesifik ternyata bisa hubung kebijakan gitu, ya, Pak, atau disatukan gitu, ya, sehingga ini kan masalah kalau
**Pak Ewin - Sesdep PMP** (117:57): Tadi kami tutup karena yang kami hasilkan itu kami sudah uji kebenarannya, gitu kan, Pak? Nah, ini tertutup berikutnya yang sudah diuji kebenarannya dan sudah dikurasi.
**Pak Ewin - Sesdep PMP** (118:21): Gitu ya, Pak. Mungkin satu tempat ini, mungkin ruang-ruangan seperti itu, Pak. Izin, Pak. Ini tentu namanya bisa gitulah, Pak, dapat kita coba diskusikan dan kita elaborasi buka ruangnya, gitu, Pak?
**Pak Ewin - Sesdep PMP** (118:33): Kami mesti jangan ini, Pak. Jangan nih kalau kami kontekalin sih, Pak, karena malam itu kita masih mengikuti meeting. Nanti biasanya dengan teman-teman di kelas Alif gitu ya?
**Pak Ewin - Sesdep PMP** (118:45): Banget gitu ya dan bagainya, kita mungkin ini kita itu pemikirkan ini, Pak, persamaannya nanti yang paling efisien efeknya, buka Pak Yunus ya. Misalnya, kalau misalnya kami punya sumber daya
**Pak Ewin - Sesdep PMP** (118:57): Ya, kloanya tertentu gitu, misalnya yang bisa ada output yang jelas itu kan mungkin malahan lebih sulit. Dan ini barang apa kita punya gitu? Mungkin.
**Pak Ewin - Sesdep PMP** (119:08): Ijin yang kita dapat, artinya kelanjutannya lebihnya kami sangat-sangat terima kasih, Pak, dan mohon depan ini kami menyita waktu Bapak. Ini bagi kami nih luar biasa, Pak. Inilah masukan-masukan karena saya senang harus diperlihatkan.
**Pak Ewin - Sesdep PMP** (119:20): Diperlukan nampaknya karena kalau misal kayak ini biasanya diangkat presentasi-presentasi PPT itu agak ni. Biasanya bingung, Pak, saya kan pembukaan. Ini seperti bikin.
**Pak Ewin - Sesdep PMP** (119:32): Nah udang?
**Pak Ewin - Sesdep PMP** (119:34): Aliran ini nanya nobainya ke sini, udah sini, waduh Mas, minta tolong bahasa manusia gitu, maksudnya tujuan kita coba lihat apa namanya?
**Pak Ewin - Sesdep PMP** (119:44): Praktek yang sudah dilakukan oleh Bapak ini menunjukkan sebenarnya hal seperti itu, jadi praktikaliti orang diperlihatkan barangnya, orang diperlihatkan ini tampanya, tantangannya ada, kita bahkan berpikir ke Yang
**Pak Ewin - Sesdep PMP** (119:56): Marli, tadi ada satu hal yang Bapak sampaikan.
**Pak Ewin - Sesdep PMP** (120:00): Kita tuh jangan sampai terpaku di ujungnya gitu, Pak Pamadani. Itu yang ini, teman-temannya, jangan terpaku di ujungnya. Bahkan mulai dari prosesnya pun didokumentasikan oleh Pak Nardhani dan tim. Saya kira ini luar biasa.
**Pak Ewin - Sesdep PMP** (120:14): Terus rempak dari dulu juga sama ini, saya mikirnya kalau sesuatu yang saya mutar ke web dan apa gitu, itu sesuatu yang sudah sifatnya di ujung, di akhir gitu, Pak, padahal sebenarnya.
**Pak Ewin - Sesdep PMP** (120:24): Semua hal kita bisa dokumentasikan, nanti itu menjadi sebenarnya akuntabilitas kita, Pak. Akuntabilitas kita, kita bisa tracking ke mana gitu ya, Pak, kalau ada kesalahan atau ada yang tidak valid, itu di titik mana, dan dia tuh terdokumentasi. Mungkin saat ini?
**Pak Ewin - Sesdep PMP** (120:38): Ada proses itu tapi manual, Pak. Yang tadi kemarin saya bilang itu, Pak, mau nyari PPT ajar luar biasa. Saya lupa di laptop di kantor atau laptop di rumah gitu. Semplay gak ada uji?
**Pak Ewin - Sesdep PMP** (120:49): Tapi kok nggak juga pada musik yang hal itu kan pilih Mas Renyah, tapi kalau kita rasakan, kita bisa refleksikan seharusnya teknologi bisa membantu kita gitu, Pak. Nah, itulah kami mau nihin Pak Mardhani dan teman-teman di ini apa biro?
**Pak Ewin - Sesdep PMP** (121:04): Transformasi digital UGM untuk kita lanjut, Pak? Tanya lanjutan, Pak, kerjasamanya. Mohon izin, nanti kami... Mohon maaf, Pak, jika ada hal-hal yang kurang berkenan, Pak, dalam ini hasil diskusi. Ini mungkin saya izinkan nantinya menu.
**Mardhani - Biro Transdig UGM** (121:19): Top ini luar biasanya, teman-teman, kalau Pak itu, hahaha.
**Mardhani - Biro Transdig UGM** (121:24): Baik, baik, terima kasih sekali, Bapak. Sebagai respon dari tadi yang sampaikan, kami tentu saja sangat senang sekali, Bapak, Ibu, kalau bisa bekerja sama.
**Mardhani - Biro Transdig UGM** (121:36): Dan juga melanjutkan diskusi ini. Jadi, bahkan nih beberapa instansi membuat WAG group khusus tampaknya ya dengan kita. Jadi untuk yang minimal komunikasi, lalu kemudian biar lebih cepat.
**Mardhani - Biro Transdig UGM** (121:48): Terima kasih, Pak. Hal-hal tertentu dan kami open, Pak, karena kami juga menjalankan proses ini. Juga bagian dari proses kita belajar juga. Nah, makin kenceng tantangan, kan? Makin
**Mardhani - Biro Transdig UGM** (122:00): Lingkat gitu ya, jadi setiap instansi itu atau organisasi bakal kami di direktorat fakultas situ sama tantangannya, sehingga itu memang menjadi pengalaman berharga juga untuk.
**Mardhani - Biro Transdig UGM** (122:12): Kita approaching, bahkan saya sampai punya pikiran kemarin itu, ini tampaknya kalau di UGM saja, Pak, ya? Itu tidak mungkin. Strateginya tuh sama untuk semua fakultas, Bu, atau semua unit kerja? Spesifik semua, jadi.
**Mardhani - Biro Transdig UGM** (122:24): Ya, itu yang harus dimainkan dari itu. Penting sekali dan saya setuju. Muka-mukanya yang kami sampaikan ini, saya malah mohon maaf, Pak, nih kalau.
**Mardhani - Biro Transdig UGM** (122:33): Ya, kalau saya memaknai dulu, bikin transformasi digital itu sebenarnya biru kocoy, Pak, meskipun ya jadi nggak bisa modalnya tuh lemeng wah doang gituan sih?
**Mardhani - Biro Transdig UGM** (122:44): Waduh, saya nggak bisa nih, gitu. Jadi, saya akhirnya minta izin, pokoknya boleh diberi ruang. Saya melakukannya dengan cara yang mungkin bahasa kerennya innovatif ini, tapi sebenarnya ya?
**Mardhani - Biro Transdig UGM** (122:56): Ya agak nah berat-nahberat gitu, tapi tadi coba jadi banyak banget yang kita terpaksa emang kali ulur, kadang mundur dulu, nggak jadi. Tapi sebenarnya seperti saya sampaikan ke Mas Dedik, itu nggak jadi, itu belum tentu jelek, cuma timing aja, Pak. Nanti pada titik
**Mardhani - Biro Transdig UGM** (123:12): Tentu lah dapat tuh momennya. Nah, kita udah punya, jadi kira-kira begitu. Jadi nggak ada ruginyalah gituloh dari kita melakukan. Jadi itu yang kami lakukan dan kami sangat mendorong nanti, mudah-mudahan.
**Mardhani - Biro Transdig UGM** (123:24): Kemenpan/Papinas juga ada yang gerak dari unit ini dan kami kalau bisa menjadi bagian dari sedikit ceritanya tuh, wah, itu satu.
**Mardhani - Biro Transdig UGM** (123:34): Panggangan yang luar biasa, Pak Miftahun di belakang, dan kami juga nih, Mbak, selain copcoy baru di belakang layar, Pak. Jadi dari organisasi itu, biasanya yang tampil ya unit pengambilnya, Mbak Akhiran gitu. Kalau kami ya sedekat apa?
**Mardhani - Biro Transdig UGM** (123:48): Jadi semacam itu. Nah, itu Bapak, bahwa Bu tadi terima kasih sekali lagi atas kedatangannya. Feel free, Pak, untuk menikmati atmosfer kami di kampus Babebu yang mungkin dulu di UGM.
**Mardhani - Biro Transdig UGM** (124:00): bisa.
**Mardhani - Biro Transdig UGM** (124:02): Nostalgia ya, lihat lagi gitu, kita perkembangannya cukup luar biasa. Mungkin beberapa sudah melihat yang di ujung sana ada apa namanya, Kiika Gelangan Inovasi Kreativitas, Musrenbang Nas, Aya Musrenbang Nasa, Astacita Indonesia Emas 2053, Prioritas Nasional, TPB/SDGs, Bappenas, Deputi, DIPA, APBN, DAK.
**Mardhani - Biro Transdig UGM** (124:12): Kelas itu student hub besar. Sebenarnya, kami sedang dalam proses juga mengestablishkan semacam launch untuk UGMAI di sana, tapi masih dalam proses. Sebetulnya, kalau nanti sudah jadi, kami
**Mardhani - Biro Transdig UGM** (124:24): Berharap event-event seperti ini bisa kami kesar ke sana karena memang itu sedikit untuk shockis gitu kan, jadi lebih baik gitu.
**Mardhani - Biro Transdig UGM** (124:32): Nih, tapi apapun itu, mohon maaf juga ada kurang-kurangan, baik gitu dari penyambutan, fasilitas, dan juga hal-hal pendukung lainnya. Semoga apa yang kami sampaikan bermanfaat. Kalau ada sedikit provokasi, memang kami by design, Pak, karena tuh tugas kami di bidang transformasi digital, ya.
**Mardhani - Biro Transdig UGM** (124:47): Jadi itu memantik gitu ya, jadi begitu. Tapi mohon maaf sekali lagi jika ada yang kurang-kurangan. Terima kasih. Nah, dan dengan demikian untuk sesi pagi ini kami tutup. Terima kasih atas hadirnya Bapak, Ibu.
**Mardhani - Biro Transdig UGM** (124:59): Semua assalamualaikum warahmatullahi wabarakatuh.
