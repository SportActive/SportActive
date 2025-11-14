--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8 (Debian 16.8-1.pgdg120+1)
-- Dumped by pg_dump version 16.9

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: announcement; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.announcement (
    id integer NOT NULL,
    title character varying(150) NOT NULL,
    content text NOT NULL,
    date character varying(20) NOT NULL,
    author character varying(80) NOT NULL
);


ALTER TABLE public.announcement OWNER TO postgres;

--
-- Name: announcement_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.announcement_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.announcement_id_seq OWNER TO postgres;

--
-- Name: announcement_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.announcement_id_seq OWNED BY public.announcement.id;


--
-- Name: event; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    date character varying(20) NOT NULL,
    image_url character varying(255),
    teams_json text,
    comment text,
    max_participants integer
);


ALTER TABLE public.event OWNER TO postgres;

--
-- Name: event_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.event_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.event_id_seq OWNER TO postgres;

--
-- Name: event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.event_id_seq OWNED BY public.event.id;


--
-- Name: event_participant; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_participant (
    id integer NOT NULL,
    event_id integer NOT NULL,
    user_id integer NOT NULL,
    join_date timestamp without time zone,
    status character varying(20)
);


ALTER TABLE public.event_participant OWNER TO postgres;

--
-- Name: event_participant_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.event_participant_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.event_participant_id_seq OWNER TO postgres;

--
-- Name: event_participant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.event_participant_id_seq OWNED BY public.event_participant.id;


--
-- Name: financial_transaction; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.financial_transaction (
    id integer NOT NULL,
    description character varying(255) NOT NULL,
    date character varying(10) NOT NULL,
    amount double precision NOT NULL,
    transaction_type character varying(20) NOT NULL,
    logged_by_admin character varying(80) NOT NULL,
    logged_at character varying(30) NOT NULL
);


ALTER TABLE public.financial_transaction OWNER TO postgres;

--
-- Name: financial_transaction_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.financial_transaction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.financial_transaction_id_seq OWNER TO postgres;

--
-- Name: financial_transaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.financial_transaction_id_seq OWNED BY public.financial_transaction.id;


--
-- Name: game_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.game_log (
    id integer NOT NULL,
    event_name character varying(100) NOT NULL,
    event_date character varying(30) NOT NULL,
    logged_at character varying(30) NOT NULL,
    active_participants_json text,
    cancelled_participants_json text,
    teams_json text,
    comment text
);


ALTER TABLE public.game_log OWNER TO postgres;

--
-- Name: game_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.game_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.game_log_id_seq OWNER TO postgres;

--
-- Name: game_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.game_log_id_seq OWNED BY public.game_log.id;


--
-- Name: poll; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.poll (
    id integer NOT NULL,
    question character varying(255) NOT NULL,
    options_json text NOT NULL,
    voted_users_json text,
    date character varying(20) NOT NULL,
    author character varying(80) NOT NULL
);


ALTER TABLE public.poll OWNER TO postgres;

--
-- Name: poll_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.poll_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.poll_id_seq OWNER TO postgres;

--
-- Name: poll_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.poll_id_seq OWNED BY public.poll.id;


--
-- Name: removed_participant_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.removed_participant_log (
    id integer NOT NULL,
    removed_user_id integer NOT NULL,
    event_id integer NOT NULL,
    admin_id integer NOT NULL,
    reason character varying(255),
    "timestamp" timestamp without time zone
);


ALTER TABLE public.removed_participant_log OWNER TO postgres;

--
-- Name: removed_participant_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.removed_participant_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.removed_participant_log_id_seq OWNER TO postgres;

--
-- Name: removed_participant_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.removed_participant_log_id_seq OWNED BY public.removed_participant_log.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    password_hash character varying(256) NOT NULL,
    role character varying(20),
    email character varying(120),
    email_confirmed boolean,
    email_confirmation_token character varying(256),
    nickname character varying(80),
    seen_items_json text
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: announcement id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcement ALTER COLUMN id SET DEFAULT nextval('public.announcement_id_seq'::regclass);


--
-- Name: event id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event ALTER COLUMN id SET DEFAULT nextval('public.event_id_seq'::regclass);


--
-- Name: event_participant id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_participant ALTER COLUMN id SET DEFAULT nextval('public.event_participant_id_seq'::regclass);


--
-- Name: financial_transaction id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.financial_transaction ALTER COLUMN id SET DEFAULT nextval('public.financial_transaction_id_seq'::regclass);


--
-- Name: game_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.game_log ALTER COLUMN id SET DEFAULT nextval('public.game_log_id_seq'::regclass);


--
-- Name: poll id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.poll ALTER COLUMN id SET DEFAULT nextval('public.poll_id_seq'::regclass);


--
-- Name: removed_participant_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.removed_participant_log ALTER COLUMN id SET DEFAULT nextval('public.removed_participant_log_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
759ba9649036
\.


--
-- Data for Name: announcement; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.announcement (id, title, content, date, author) FROM stdin;
9	ПРАВИЛА	Правила прості. Ніхто нікого ні до чого не примушує. Ми створюємо простір, де можемо поспілкуватись, разом активно провести час. Кожен може запропонувати ідею і знайти однодумців.\r\n\r\nМи проводили пікніки, катались на велосипедах, на сапах, грали у волейбол, бадмінтон, теніс, пінг-понг, піклбол. Далі - буде...\r\n\r\nЯк стати учасником - досить просто. Зв'язатись з адміністраторами https://chat.whatsapp.com/HEdv3OLrTS6IDw7It8Rf7x\r\n\r\nДля того, щоб ми могли грати у приміщенні, закупляти призи на замагання, організовувати активності і закупляти інвентар - нам потрібні гроші. Фінансовий звіт ми викладаємо тут кожного місяця. Тому учасники клубу сплачують 10 ф. на місяць. А організатори, зі свого боку, майже стовідсотково нададуть вам змогу пограти хоча б раз на тиждень у закритому приміщенні (а також - тенісний корт). На жаль, на зараз наші можливості обмежені двома кортами на день максимум.\r\n\r\nЯк дізнатись коли і з ким можна пограти.\r\nДля цього ми зробили додаток, в який додали розклад ігор в найбільш поширений час. \r\nhttps://ua-sport-active-kent.up.railway.app/\r\nЯкщо у вас є побажання провести гру у інший час (не одноразово, а на постійній основі), проведіть опитування (приватно, або в групі) і, якщо знайдеться необхідна кількість учасників - ми додамо цей час в наш розклад.\r\n\r\nЯк правильно записатись на гру. В кінці тижня ми викладаємо розклад на наступний тиждень. Записуйтесь на гру в ті дні, в які ви можете грати (навіть, якщо це буде 6 днів на тиждень). Для організаторів це дає можливість комбінувати склад учасників, враховувати індивідуальні особливості і інші нюанси. Але пам'ятайте, що ви можете грати як 6 днів, якщо будуть вільні місця, так і 1 день - той, який ми точно зможемо організувати. (Ми найближчим часом додамо статистику і організатори зможуть більш рівномірно розподіляти ігри для тих хто грає часто).\r\nЩо ми робимо, коли на гру записалось більше, ніж може грати.\r\n1. Новачок. Для того, хто вперше приходить на знайомство з грою ми надаємо таку перевагу, як комплімент від учасників клубу.\r\n2. Внески. Перевага тим, хто сплатив внесок\r\n3. Кількість ігор на тижні. Перевага тому, хто грав менше\r\n4. Черга. Перевага тому, хто записався раніше.\r\n\r\nМеленький нюанс. Якщо ви зареєструвались і згадали, що в якийсь день не зможете - ви можете відмовитись від гри. Якщо відмовитесь більше ніж через годину після реєстрації, то зі списку ви не зникнете, а навпроти вас буде відповідна помітка.	2025-10-12 19:43:31	Кирило
10	Звіт за жовтень	Баланс на початок\r\n136.00\r\n\r\nНадходження\r\n+ 160.00 \r\n\r\nВитрати\r\n- 172.00 \r\n60 + 20 - мембершип\r\n92 - призи на турнір\r\n\r\nБаланс на кінець\r\n124.00 	2025-11-08 17:56:37	Кирило
1	Фінансовий звіт за червень 2025	Початковий залишок з попереднього періоду: 30 ф.\r\nМи отримали членських внесків:             70 ф. + 20 ф. на рахунок ком'юніті\r\nОплата членських внесків бадмінтон:        10 + 62 = 72 ф.\r\nОплата членських внесків теніс:            40 ф. (Оля Макмахон купила                               мембершіп, але відмовилась взяти компенсацію)  \r\nЗалишок в касі:                            8 ф.    \r\n                 	2025-07-02 20:19:26	Кирило
3	Нова адреса додатку!	Друзі!\r\nОскільки безкоштовний веб-сервіс, яким я користувався для розробки додатку запускався повільно, я перевів його на трошки платну версію. Адреса його змінилась на \r\n\r\nhttps://ua-sport-active-kent.up.railway.app/\r\n\r\nСтара адреса теж залишається активною поки що.\r\nМайте на увазі, якщо ви зберігали пароль в менеджері паролів гугл, то для нової адреси цей пароль потрібно буде повторити вручну. \r\nСподіваюсь, це не викличе у вас труднощів.\r\nНу і якщо ви створювали ярлик для додатку, його теж потрібно буде повторити.	2025-07-26 22:28:27	Кирило
4	Фінансовий звіт за липень 2025	Баланс на початок\r\n8.00\r\n\r\nНадходження\r\n+ 195.00 - членські внески\r\n\r\nВитрати\r\n- 94.00 = 15 (тенісні м'ячі), 79 (корти бадмінтон)\r\n\r\nБаланс на кінець\r\n109.00 (з них 45 - на рахунку ком'юніті)	2025-08-04 21:14:55	Кирило
5	Зміни розкладу	Друзі, гарного всім настрою!\r\nПочинається новий сезон у школі, наступають зміни в особистих розкладах учасників ))).\r\nЯ вже вніс розклад на наступний тиждень. Хотів на початку зробити опитування, а потім вирішив, що більш наочно буде побачити це саме в розкладі.\r\nЩо там змінено:\r\nДодана ще дві гри Бадмінтон у понеділок о 19:00 і у п'ятницю о 18:00 (для тих, хто буде відводити дітей на українські заняття має бути зручно). Це не означає, що бадмінтон буде кожен день, скоріш за все він залишиться як і раніше - тричі на тиждень (бо кількість учасників поки не збільшилась).\r\nГру у Теніс поки що залишив без змін, теж у п'ятницю о 18:00. Її потрібно б було, перенести, або додати ще одну, але поки не знаю куди і як, може ви щось запропонуєте...\r\n\r\nНагадаю. \r\nПоставте всі можливі варіанти вашого відвідування. Ми розплануємо так, щоб кожен міг пограти хоча б одну гру на тиждень. Чим більше у вас є можливостей відвудувати гру, тим легше нам буде спланувати потреби.	2025-09-10 11:09:47	Кирило
6	Проведення турніру	Всіх запрошуємо приєднатись до участі у турнірі. Записатись легко - знайти опитування у вотсап-групі і поставити там свій голос.\r\n\r\nОскільки це турнір, маємо позмагатись!). Турнір буде у змішаних парах. Пари будуть визначені шляхом відбору.	2025-09-10 12:01:25	Кирило
7	Фінансовий звіт за серпень	Баланс на початок\r\n109.00\r\n\r\nНадходження\r\n+ 110.00\r\n\r\nВитрати\r\n- 80.00 (це оплата мембершипів)\r\n\r\nБаланс на кінець\r\n139.00	2025-10-10 11:38:53	Кирило
8	Фінансовий звіт за вересень	Баланс на початок\r\n139.00\r\n\r\nНадходження\r\n+ 130.00\r\n\r\nВитрати\r\n- 133.00 (80 - мембершипи, 53 - волани)\r\n\r\nБаланс на кінець\r\n136.00	2025-10-10 11:43:42	Кирило
\.


--
-- Data for Name: event; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event (id, name, date, image_url, teams_json, comment, max_participants) FROM stdin;
122	Бадмінтон	2025-11-21 10:00:00	\N	{}		\N
123	Бадмінтон	2025-11-17 19:00:00	\N	{}		\N
125	Бадмінтон	2025-11-19 20:00:00	\N	{}	Граємо о 20:00‼️	\N
126	Бадмінтон  	2025-11-20 20:00:00	\N	{}	В четвер граємо о 20:00‼️\r\n\r\nКрасивая і Jozefina та інші, кого ми не знаємо. Будь ласка, вийдіть на контакт з адміністраторами клубу, щоб ми могли розуміти, хто ви є, чи ознайомлені ви з правилами і який у вас рівень гри.	\N
124	Бадмінтон	2025-11-18 19:00:00	\N	{}	Красивая і Jozefina та інші, кого ми не знаємо. Будь ласка, вийдіть на контакт з адміністраторами клубу, щоб ми могли розуміти, хто ви є, чи ознайомлені ви з правилами і який у вас рівень гри.	\N
\.


--
-- Data for Name: event_participant; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_participant (id, event_id, user_id, join_date, status) FROM stdin;
178	126	2	2025-11-13 22:12:19.802718	active
179	125	31	2025-11-13 22:47:11.389864	active
180	123	42	2025-11-13 22:50:06.408014	active
181	125	42	2025-11-13 22:50:22.440567	active
182	124	48	2025-11-13 22:53:15.304559	active
183	126	48	2025-11-13 22:53:32.293096	active
184	124	23	2025-11-14 04:12:11.422344	active
185	126	17	2025-11-14 09:16:09.918922	active
186	126	46	2025-11-14 09:37:47.451385	active
187	123	31	2025-11-14 09:55:29.765502	active
188	123	11	2025-11-14 14:34:29.912046	active
189	125	11	2025-11-14 14:34:33.111836	active
190	124	9	2025-11-14 14:40:44.278359	active
191	126	9	2025-11-14 14:40:51.541398	active
192	124	20	2025-11-14 14:52:40.929548	active
194	126	20	2025-11-14 14:53:34.997884	active
195	124	14	2025-11-14 14:53:36.26769	active
196	126	14	2025-11-14 14:53:42.288136	active
197	122	40	2025-11-14 14:55:21.117854	active
198	123	12	2025-11-14 14:56:18.582531	active
199	125	12	2025-11-14 14:56:30.671797	active
201	124	5	2025-11-14 15:09:03.340164	active
202	126	5	2025-11-14 15:09:32.767643	active
203	124	16	2025-11-14 15:17:00.400646	active
204	123	16	2025-11-14 15:52:27.980335	active
205	124	21	2025-11-14 16:01:47.74177	active
206	126	21	2025-11-14 16:01:52.79589	active
209	123	51	2025-11-14 16:07:37.336022	active
210	125	51	2025-11-14 16:07:41.264409	active
211	123	30	2025-11-14 16:20:37.053639	active
200	124	12	2025-11-14 14:57:02.19187	refused
212	125	26	2025-11-14 17:53:53.492531	active
213	123	26	2025-11-14 17:54:19.283296	active
214	124	26	2025-11-14 17:54:38.848689	active
215	125	32	2025-11-14 18:12:56.66593	active
216	124	29	2025-11-14 18:40:29.044428	active
217	126	29	2025-11-14 18:40:51.297839	active
220	122	37	2025-11-14 19:40:07.083299	active
221	125	37	2025-11-14 19:41:08.610785	active
208	126	50	2025-11-14 16:02:35.307906	removed
219	126	52	2025-11-14 19:25:04.680531	removed
218	124	52	2025-11-14 19:24:56.387128	removed
207	124	50	2025-11-14 16:02:27.586368	removed
222	124	53	2025-11-14 20:11:14.417905	removed
223	126	53	2025-11-14 20:11:25.431165	removed
\.


--
-- Data for Name: financial_transaction; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.financial_transaction (id, description, date, amount, transaction_type, logged_by_admin, logged_at) FROM stdin;
2	Баланс на початок	2025-06-30	8	income	Кирило	2025-07-05 22:23:35
4	Оплата мембершіп Юля	2025-07-05	-59	expense	Кирило	2025-07-05 23:15:58
1	Членський внесок (2025-07) від Anna	2025-07-02	25	income	Кирило	2025-07-05 22:23:04
51	Членський внесок (2025-09) від Наталія Овсієнко 	2025-09-04	10	income	Кирило	2025-09-04 18:03:13
14	Членський внесок (2025-07) від Olga Mc	2025-07-05	10	income	Кирило	2025-07-06 10:54:07
15	Членський внесок (2025-07) від Vitalij	2025-07-05	10	income	Кирило	2025-07-06 15:41:57
16	Членський внесок (2025-07) від Olha D	2025-07-05	10	income	Кирило	2025-07-06 15:45:07
17	Членський внесок (2025-07) від Olena A	2025-07-05	10	income	Кирило	2025-07-06 15:45:40
18	Членський внесок (2025-07) від Karyna	2025-07-01	10	income	Кирило	2025-07-06 15:45:58
19	Членський внесок (2025-06) від Vitalij	2025-07-05	10	income	Кирило	2025-07-06 16:56:04
20	Членський внесок (2025-07) від Хтось	2025-07-05	10	income	Кирило	2025-07-06 17:20:37
21	Членський внесок (2025-07) від helga_r80@icloud.com	2025-07-05	10	income	Кирило	2025-07-06 17:21:07
22	Членський внесок (2025-07) від Ruslan R.	2025-07-05	10	income	Кирило	2025-07-06 17:21:43
23	Членський внесок (2025-07) від Наталія Овсієнко 	2025-07-10	10	income	Кирило	2025-07-10 20:11:05
24	Членський внесок (2025-07) від Світлана	2025-07-05	10	income	Кирило	2025-07-10 20:13:31
25	Членський внесок (2025-07) від Jeff	2025-07-05	10	income	Кирило	2025-07-10 20:13:51
26	Оплата мембершип Оля	2025-07-03	-20	expense	Кирило	2025-07-10 20:21:54
27	Членський внесок (2025-07) від Ilona	2025-07-01	10	income	Кирило	2025-07-13 20:08:36
28	Членський внесок (2025-07) від Gedeon347	2025-07-15	10	income	Кирило	2025-07-15 19:10:09
29	Членський внесок (2025-07) від Oleksandra 	2025-07-15	10	income	Кирило	2025-07-15 19:10:34
30	М'ячі	2025-07-19	-15	expense	Кирило	2025-07-19 12:45:05
31	Членський внесок (2025-08) від Olga Mc	2025-07-29	10	income	Кирило	2025-07-29 18:56:53
32	Членський внесок (2025-09) від Olga Mc	2025-07-29	10	income	Кирило	2025-07-29 18:57:14
33	Членський внесок (2025-08) від Jeff	2025-08-05	10	income	Кирило	2025-08-05 18:01:36
34	Членський внесок (2025-08) від tmbmax	2025-08-05	10	income	Кирило	2025-08-05 18:02:00
35	Членський внесок (2025-08) від Karyna	2025-08-05	10	income	Кирило	2025-08-05 18:02:30
36	Оплата мембершіп Юля	2025-08-05	-60	expense	Кирило	2025-08-06 15:03:15
37	Членський внесок (2025-08) від Ilona	2025-08-06	10	income	Кирило	2025-08-06 17:56:45
38	Членський внесок (2025-08) від Oleksandra 	2025-08-06	10	income	Кирило	2025-08-06 19:01:45
39	Членський внесок (2025-08) від Gedeon347	2025-08-06	10	income	Кирило	2025-08-06 19:02:01
40	Членський внесок (2025-08) від Anna	2025-08-06	10	income	Кирило	2025-08-06 19:02:17
41	Членський внесок (2025-08) від Olena A	2025-08-06	10	income	Кирило	2025-08-06 19:03:31
42	Членський внесок (2025-08) від Olha D	2025-08-13	10	income	Кирило	2025-08-15 14:11:30
43	Оплата мембершіп Оля	2025-08-13	-20	expense	Кирило	2025-08-15 14:11:55
44	Членський внесок (2025-08) від helga_r80@icloud.com	2025-08-13	10	income	Кирило	2025-08-15 14:12:41
45	Членський внесок (2025-08) від Ruslan R.	2025-08-13	10	income	Кирило	2025-08-15 14:13:02
46	Членський внесок (2025-09) від Anna	2025-09-02	10	income	Кирило	2025-09-02 20:35:54
47	Членський внесок (2025-09) від helga_r80@icloud.com	2025-09-02	10	income	Кирило	2025-09-02 21:30:50
48	Членський внесок (2025-09) від Ruslan R.	2025-09-02	10	income	Кирило	2025-09-02 21:31:22
49	Частково оплата Юлі за мембершип	2025-09-02	-20	expense	Кирило	2025-09-02 21:32:23
50	Членський внесок (2025-09) від Vitalij	2025-09-04	10	income	Кирило	2025-09-04 18:02:43
53	Членський внесок (2025-09) від tmbmax	2025-09-09	10	income	Кирило	2025-09-09 21:38:08
54	Частково оплата Олі за мембершип	2025-09-09	-20	expense	Кирило	2025-09-09 21:39:42
55	Членський внесок (2025-09) від Olha D	2025-09-09	10	income	Кирило	2025-09-09 21:40:10
56	Членський внесок (2025-09) від Karyna	2025-09-11	10	income	Кирило	2025-09-11 07:41:36
57	Членський внесок (2025-09) від Ilona	2025-09-17	10	income	Кирило	2025-09-17 19:02:18
58	Членський внесок (2025-10) від Vitalij	2025-09-18	10	income	Кирило	2025-09-18 17:55:38
59	Членський внесок (2025-09) від Jeff	2025-09-25	10	income	Кирило	2025-09-25 19:59:45
60	Членський внесок (2025-09) від Світлана	2025-09-25	10	income	Кирило	2025-09-25 20:00:29
61	покупка воланів з фонду ком'юніті	2025-09-22	-53	expense	Кирило	2025-09-25 20:01:34
62	Членський внесок (2025-09) від Dmamp	2025-09-27	10	income	Кирило	2025-09-27 19:14:44
63	Членський внесок (2025-10) від Dmamp	2025-10-03	10	income	Кирило	2025-10-03 10:52:10
64	Оплата Юлі за мембершип	2025-10-03	-60	expense	Кирило	2025-10-03 10:52:53
65	Членський внесок (2025-10) від Ilona	2025-10-04	10	income	Кирило	2025-10-04 11:44:25
66	Членський внесок (2025-10) від Наталія Овсієнко 	2025-10-04	10	income	Кирило	2025-10-04 11:46:52
67	Членський внесок (2025-10) від bakumvv@gmail.com	2025-10-04	10	income	Кирило	2025-10-04 12:05:39
68	Членський внесок (2025-09) від Хтось	2025-10-04	10	income	Кирило	2025-10-04 12:05:55
69	Членський внесок (2025-10) від Хтось	2025-10-04	10	income	Кирило	2025-10-04 12:06:09
70	Призи для турніру	2025-10-05	-92	expense	Кирило	2025-10-05 16:26:47
71	Членський внесок (2025-10) від Karyna	2025-10-06	10	income	Кирило	2025-10-06 07:44:31
72	Членський внесок (2025-10) від tmbmax	2025-10-07	10	income	Кирило	2025-10-07 08:40:53
73	Членський внесок (2025-10) від helga_r80@icloud.com	2025-10-09	10	income	Кирило	2025-10-09 19:10:26
74	Членський внесок (2025-10) від Ruslan R.	2025-10-09	10	income	Кирило	2025-10-09 19:10:56
75	Членський внесок (2025-11) від Vitalij	2025-10-09	10	income	Кирило	2025-10-09 19:11:19
76	Членський внесок (2025-10) від Olha D	2025-10-06	10	income	Кирило	2025-10-10 11:34:38
77	Частково оплата Олі за мембершип	2025-10-06	-20	expense	Кирило	2025-10-10 11:35:23
52	Оплата мембершіп Юля	2025-09-06	-40	expense	Кирило	2025-09-07 14:27:01
79	Членський внесок (2025-10) від Olena A	2025-10-10	10	income	Кирило	2025-10-10 15:36:22
80	Членський внесок (2025-10) від Anna	2025-10-18	10	income	Кирило	2025-10-18 11:19:53
81	Членський внесок (2025-10) від Jeff	2025-10-27	10	income	Кирило	2025-10-27 09:02:49
82	Членський внесок (2025-10) від Світлана	2025-10-27	10	income	Кирило	2025-10-27 09:03:36
83	Членський внесок (2025-11) від Віталій	2025-11-02	10	income	Кирило	2025-11-02 18:06:45
84	Членський внесок (2025-11) від Karyna	2025-11-08	10	income	Кирило	2025-11-08 17:53:17
85	Членський внесок (2025-11) від Olena A	2025-11-08	10	income	Кирило	2025-11-08 17:53:39
86	Членський внесок (2025-11) від tmbmax	2025-11-08	10	income	Кирило	2025-11-08 17:54:15
88	Членський внесок (2025-11) від Ruslan R.	2025-11-10	10	income	Кирило	2025-11-10 09:52:24
89	Членський внесок (2025-11) від Olha D	2025-11-10	10	income	Кирило	2025-11-10 18:19:21
90	Членський внесок (2025-11) від helga_r80@icloud.com	2025-11-10	10	income	Кирило	2025-11-10 18:19:42
91	Оплата мембершіп Юля	2025-11-10	-60	expense	Кирило	2025-11-10 18:20:11
92	Оплата мембершіп Оля Д	2025-11-10	-20	expense	Кирило	2025-11-10 18:20:37
93	Членський внесок (2025-11) від Jeff	2025-11-12	10	income	Кирило	2025-11-12 22:31:38
94	Членський внесок (2025-11) від Uliana	2025-11-12	10	income	Кирило	2025-11-12 22:32:05
95	Членський внесок (2025-11) від Світлана	2025-11-12	10	income	Кирило	2025-11-12 22:32:53
96	Членський внесок (2025-11) від Maria	2025-11-12	10	income	Кирило	2025-11-12 22:33:13
97	Членський внесок (2025-11) від Наталія Овсієнко 	2025-11-12	10	income	Кирило	2025-11-14 16:02:04
\.


--
-- Data for Name: game_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.game_log (id, event_name, event_date, logged_at, active_participants_json, cancelled_participants_json, teams_json, comment) FROM stdin;
1	Бадминтон	2025-07-03 19:00:00	2025-07-03 20:02:16	["Кирило"]	[]	{"Сонечки": ["Кирило"]}	\N
2	Теніс	2025-07-04 19:00:00	2025-07-04 20:25:26	["Кирило"]	["Anna"]	{"Сонечки": ["Кирило"], "Метелики": []}	\N
3	Волейбол	2025-07-05 17:00:00	2025-07-05 22:20:31	[]	["Кирило"]	{"Сонечки": []}	\N
4	Теніс	2025-07-06 18:00:00	2025-07-06 18:31:41	["Anna", "Nadiia Johnson"]	[]	{}	Граємо разом
5	Бадминтон	2025-07-08 19:00:00	2025-07-08 21:08:53	["Кирило", "Olga Mc", "helga_r80@icloud.com", "Ruslan R.", "Oleksandra ", "Gedeon347"]	[]	{"Метелики": ["Кирило", "Olga Mc", "helga_r80@icloud.com", "Ruslan R."]}	Може бути змінено в залежності від кількості і складу учасників. Обирайте всі можливі варіанти
6	Бадминтон	2025-07-09 19:00:00	2025-07-09 19:17:59	["Anna", "Olha D", "Olena A", "Vitalij", "Хтось", "Yuliia P", "Світлана", "Jeff"]	["Кирило"]	{"Метелики": ["Olha D", "Olena A", "Світлана", "Jeff"], "Крафті": ["Anna", "Vitalij", "Хтось", "Yuliia P"]}	Може бути змінено в залежності від кількості і складу учасників. Обирайте всі можливі варіанти
7	Бадминтон	2025-07-10 19:00:00	2025-07-10 19:30:06	["Кирило", "Vitalij", "Karyna", "Наталія Овсієнко ", "Olha D"]	[]	{}	Може бути змінено в залежності від кількості і складу учасників. Обирайте всі можливі варіанти
8	Теніс	2025-07-11 19:00:00	2025-07-11 20:44:42	["Кирило", "Хтось", "Ruslan R.", "helga_r80@icloud.com", "Olga Mc"]	["Vitalij"]	{}	
9	Волейбол	2025-07-12 17:00:00	2025-07-12 17:29:41	["Кирило", "Vitalij", "Хтось"]	[]	{}	Відміняємо волейбол, бо частина поїхала на лаванду, а в трьох грати не цікаво...
10	Теніс	2025-07-13 18:00:00	2025-07-13 18:04:48	["Nadiia Johnson"]	[]	{}	
11	Бадмінтон	2025-07-15 19:00:00	2025-07-15 19:09:22	["Oleksandra ", "Кирило", "Karyna", "Gedeon347"]	[]	{"Корт 2": ["Oleksandra", "Кирило", "Karyna", "Gedeon347"]}	
12	Бадмінтон	2025-07-16 19:00:00	2025-07-16 20:16:26	["Olha D", "helga_r80@icloud.com", "Ruslan R.", "Vitalij", "Хтось", "Світлана", "Jeff", "Karyna", "Anna", "Olga Mc"]	[]	{"Грає в інший день": ["Vitalij", "Karyna"], "Корт 2": ["Olha D", "Світлана", "Jeff", "Olga Mc"], "Корт 3": ["helga_r80@icloud.com", "Ruslan R.", "Хтось", "Anna"]}	
13	Бадмінтон	2025-07-17 19:00:00	2025-07-17 20:00:30	["Кирило", "Наталія Овсієнко ", "Vitalij", "Karyna"]	[]	{"Корт 1": ["Кирило", "Наталія Овсієнко", "Vitalij", "Karyna"]}	
14	Теніс	2025-07-18 19:00:00	2025-07-18 19:21:13	["Кирило", "Ilona", "Хтось"]	["Olga Mc"]	{}	
15	Волейбол	2025-07-19 17:00:00	2025-07-20 14:48:02	["Кирило", "Наталія Овсієнко "]	[]	{}	Гру відміняємо. Бо після свята Абетки нікого зібрати не можу
16	Теніс	2025-07-20 18:00:00	2025-07-20 18:05:08	["Nadiia Johnson"]	[]	{}	
17	Бадмінтон	2025-07-23 19:00:00	2025-07-23 22:35:28	["Світлана", "Jeff", "Olga Mc", "Anna"]	["Наталія Овсієнко "]	{}	Пройдіть опитування, якщо хочете змінити час гри з 19:00 на 18:00
18	Бадмінтон	2025-07-24 19:00:00	2025-07-24 19:54:35	["Наталія Овсієнко ", "Ilona", "Ruslan R.", "Olena A"]	[]	{}	Пройдіть опитування, якщо хочете змінити час гри з 19:00 на 18:00
19	Теніс	2025-07-25 19:00:00	2025-07-26 22:12:39	["Кирило", "Ruslan R.", "Olha D", "Olga Mc"]	["Ilona"]	{}	Пройдіть опитування, якщо хочете змінити час гри з 19:00 на 18:00
20	Волейбол	2025-07-26 17:00:00	2025-07-26 22:12:39	["Наталія Овсієнко "]	[]	{}	
21	Теніс	2025-07-27 18:00:00	2025-07-27 19:28:54	[]	[]	{}	
22	Бадмінтон	2025-07-24 19:00:00	2025-07-27 20:57:52	[]	[]	{}	
23	Бадмінтон	2025-07-24 19:00:00	2025-07-27 20:58:29	[]	[]	{}	
24	Бадмінтон	2025-07-29 20:00:00	2025-07-29 20:15:03	["Кирило", "Olga Mc", "Ilona", "Anna"]	[]	{}	УВАГА! Зміна часу!!!\r\nНа 17, 18,19 годин корти всі вже зайняті. Тому букаємо корт на 20:00
25	Бадмінтон	2025-07-30 19:00:00	2025-07-30 19:15:39	["Кирило", "Anna", "Olha D", "Olena A"]	[]	{}	
26	Бадмінтон	2025-07-31 19:00:00	2025-07-31 21:41:56	["Karyna", "Світлана", "Jeff"]	["Кирило", "tmbmax"]	{}	
27	Теніс	2025-08-01 19:00:00	2025-08-01 19:27:51	["Кирило", "Olga Mc", "Ilona", "tmbmax"]	["Olha D"]	{}	Ми знову змінили час на 19:00 ))). \r\n\r\n
28	Бадмінтон  	2025-08-05 19:00:00	2025-08-05 19:53:52	["tmbmax", "Jeff", "Karyna", "Кирило", "helga_r80@icloud.com"]	[]	{"Грає в інший день": ["helga_r80@icloud.com"]}	
29	Бадмінтон  	2025-08-06 19:00:00	2025-08-06 19:47:21	["Ilona", "Olena A", "Oleksandra ", "Gedeon347", "Olga Mc", "Jeff", "Karyna", "Anna", "Yuliia P", "Кирило"]	[]	{"Корт 4": ["Oleksandra", "Gedeon347", "Olga Mc"], "Грає в інший день": ["Jeff", "Karyna"], "Корт 5": ["Ilona", "Olena A", "Anna", "Yuliia P"], "замість мене - Вікторія, корт 4": ["Кирило"]}	
30	Бадмінтон  	2025-08-07 19:00:00	2025-08-08 08:03:29	["tmbmax", "Karyna", "helga_r80@icloud.com", "Ruslan R."]	[]	{"Корт 4": ["tmbmax", "Karyna", "helga_r80@icloud.com", "Ruslan R."]}	
31	Теніс	2025-08-08 19:00:00	2025-08-08 21:18:01	["tmbmax", "Olga Mc", "Jeff", "Кирило", "Yuliia P", "Karyna", "Ilona"]	[]	{}	
32	Бадмінтон  	2025-08-12 19:00:00	2025-08-12 19:11:53	["Кирило", "Ilona", "Jeff", "Karyna", "tmbmax", "Olha D"]	["Yuliia P", "Olga Mc"]	{"Корт 2": ["tmbmax", "Olha D", "Ilona", "Кирило", "Jeff"], "Грає в інший день": ["Karyna"]}	
33	Бадмінтон  	2025-08-13 19:00:00	2025-08-14 07:46:01	["Кирило", "Jeff", "helga_r80@icloud.com", "Ruslan R."]	[]	{}	
66	Бадмінтон	2025-10-01 19:00:00	2025-10-01 19:34:34	["tmbmax", "Хтось", "Karyna", "Наталія Овсієнко ", "Світлана", "Jeff", "Anna"]	["Ruslan R.", "Віталій"]	{}	
34	Бадмінтон  	2025-08-14 19:00:00	2025-08-14 20:00:59	["Кирило", "Olga Mc", "Jeff"]	["Ilona"]	{"Грає в інший день": ["Jeff", "Olga Mc", "Кирило"]}	Увага! Ми відміняємо гру в цей день. Перебудуйте ваші плани.
35	Теніс	2025-08-15 19:00:00	2025-08-17 18:03:41	["Yuliia P", "Olga Mc", "Jeff", "tmbmax"]	["Кирило", "Ilona"]	{}	
36	Бадмінтон	2025-08-19 19:00:00	2025-08-19 20:58:59	["tmbmax", "helga_r80@icloud.com", "Ruslan R.", "Olha D", "Ilona", "Світлана", "Jeff", "Кирило"]	[]	{"Грає в інший день": ["helga_r80@icloud.com", "Ruslan R.", "Світлана", "Jeff"], "Корт 3": ["tmbmax", "Olha D", "Ilona", "Кирило"]}	
37	Бадмінтон	2025-08-20 19:00:00	2025-08-20 19:00:06	[]	[]	{}	
38	Бадмінтон	2025-08-21 19:00:00	2025-08-21 21:19:38	["helga_r80@icloud.com", "Ruslan R.", "Світлана", "Jeff"]	[]	{}	
39	Теніс	2025-08-22 19:00:00	2025-08-22 19:43:45	[]	["tmbmax"]	{}	
40	Бадмінтон  	2025-08-26 19:00:00	2025-08-26 19:39:46	["helga_r80@icloud.com", "Olha D", "tmbmax", "Ruslan R.", "Olga Mc"]	[]	{}	
41	Бадмінтон  	2025-08-27 19:00:00	2025-08-27 19:36:53	["Karyna"]	["Світлана"]	{}	
42	Бадмінтон  	2025-08-28 20:00:00	2025-08-29 08:24:56	["helga_r80@icloud.com", "Ruslan R.", "Karyna", "Olha D"]	[]	{}	
43	Теніс	2025-08-29 19:00:00	2025-08-30 17:21:31	["tmbmax", "Хтось", "Ilona"]	["Olga Mc"]	{}	
44	Бадмінтон  	2025-09-02 19:00:00	2025-09-02 19:08:37	["helga_r80@icloud.com", "Ruslan R."]	[]	{"Корт 2": ["Ruslan R.", "helga_r80@icloud.com"]}	
45	Бадмінтон  	2025-09-03 19:00:00	2025-09-04 07:37:26	["Віталій", "Olga Mc", "Хтось", "Anna"]	["Кирило", "helga_r80@icloud.com"]	{"Корт 1": ["Віталій", "Olga Mc", "Хтось", "Anna"]}	
46	Бадмінтон  	2025-09-04 19:00:00	2025-09-04 20:06:57	["Кирило", "Віталій", "Karyna", "Наталія Овсієнко "]	[]	{"Корт 4": ["Наталія Овсієнко", "Karyna", "Віталій", "Кирило"]}	
47	Теніс	2025-09-05 19:00:00	2025-09-05 19:12:35	["Кирило", "Olga Mc", "Хтось", "tmbmax"]	[]	{}	
48	Бадмінтон	2025-09-09 19:00:00	2025-09-09 19:07:40	["Кирило", "helga_r80@icloud.com", "Olga Mc", "Ruslan R."]	["Віталій"]	{}	
49	Бадмінтон	2025-09-10 19:00:00	2025-09-10 19:13:01	["Кирило", "Karyna", "Віталій", "Anna", "Хтось"]	["Наталія Овсієнко "]	{"Грає в інший день": ["Кирило"]}	Друзі, час - 19:00!!!\r\nБуває, що коли вношу гру, можу не додивитись час. Час у нас поки що один - 19:00. Окрім гри на вулиці - там 18:00.\r\nЯкщо бачите, що час відрізняється - повідомте мені, я виправлю.\r\n
50	Бадмінтон	2025-09-11 19:00:00	2025-09-11 19:03:23	["Ilona", "Кирило", "tmbmax", "helga_r80@icloud.com", "Наталія Овсієнко "]	[]	{"Грає в інший день": ["Кирило"]}	
51	Теніс	2025-09-12 18:00:00	2025-09-12 18:48:05	["Кирило", "Хтось", "tmbmax"]	[]	{}	ВІДМІНА !!!\r\n\r\nЗ погодних умов відміняємо гру.Сильний вітер
52	Бадмінтон	2025-09-15 19:00:00	2025-09-15 20:17:59	[]	["Ilona"]	{}	
53	Бадмінтон	2025-09-16 19:00:00	2025-09-16 19:26:38	["Кирило", "helga_r80@icloud.com", "Наталія Овсієнко ", "Ruslan R.", "tmbmax"]	[]	{"Грає в інший день": ["Кирило"]}	
54	Бадмінтон	2025-09-17 19:00:00	2025-09-17 19:01:23	["Віталій", "Кирило", "Наталія Овсієнко ", "Anna", "Хтось", "Karyna", "Ilona"]	["Olha D", "helga_r80@icloud.com"]	{}	
55	Бадмінтон	2025-09-18 19:00:00	2025-09-18 20:38:38	["Віталій", "Кирило", "Karyna", "bakumvv@gmail.com", "Yuliia P", "Olha D", "helga_r80@icloud.com", "tmbmax", "Anna"]	["Наталія Овсієнко "]	{"Грає в інший день": ["Наталія Овсієнко", "Anna"]}	Наталі грає в інший день.
56	Теніс	2025-09-19 18:00:00	2025-09-20 10:54:35	["Кирило", "Olga Mc"]	["Ilona"]	{}	
57	Бадмінтон	2025-09-19 18:00:00	2025-09-20 10:54:35	["Кирило", "Віталій", "Anna", "Yuliia P", "bakumvv@gmail.com", "tmbmax"]	[]	{}	ВІДМІНА!!!\r\nДрузі, у вечір п'ятниці ми не можемо забукати корти - вони просто недоступні від самого початку. Нажаль.\r\n
58	Бадмінтон  	2025-09-23 19:00:00	2025-09-23 19:05:27	["Ilona", "tmbmax", "Кирило", "Наталія Овсієнко ", "Ruslan R.", "helga_r80@icloud.com"]	["Olga Mc"]	{"Грає в інший день": ["Ruslan R.", "helga_r80@icloud.com"]}	
59	Бадмінтон  	2025-09-24 19:00:00	2025-09-24 19:40:20	["Karyna", "tmbmax", "Наталія Овсієнко ", "Ruslan R.", "Anna", "Віталій", "Хтось", "Світлана", "Jeff"]	[]	{"Грає в інший день": ["Ruslan R."]}	
60	Бадмінтон  	2025-09-25 19:00:00	2025-09-25 19:12:23	["Yuliia P", "tmbmax", "Кирило", "Karyna", "Ruslan R.", "helga_r80@icloud.com", "Віталій", "Світлана", "Jeff"]	[]	{"Грає в інший день": ["Karyna", "Кирило", "tmbmax"]}	
61	Бадмінтон  	2025-09-26 10:00:00	2025-09-26 10:19:05	["Кирило", "Ilona", "Yuliia P", "Dmamp"]	[]	{}	
62	Теніс	2025-09-26 18:00:00	2025-09-26 19:14:39	["tmbmax", "Хтось"]	["Ilona", "Кирило", "Dmamp"]	{}	Теніс ми відміняємо на сьогодні!
63	Бадмінтон  	2025-09-28 16:00:00	2025-09-28 16:19:35	["tmbmax", "Yuliia P", "Karyna", "Dmamp", "helga_r80@icloud.com", "Jeff", "Світлана"]	["Ruslan R."]	{}	
64	Бадмінтон	2025-09-29 19:00:00	2025-09-29 20:08:47	["tmbmax", "Karyna", "Наталія Овсієнко ", "Ilona"]	["Ruslan R."]	{}	
65	Бадмінтон	2025-09-30 19:00:00	2025-09-30 19:38:04	["Ruslan R.", "tmbmax", "helga_r80@icloud.com", "Наталія Овсієнко ", "Jeff", "Світлана", "Maria", "George", "Karyna"]	[]	{"Грає в інший день": ["tmbmax"]}	
67	Бадмінтон	2025-10-02 19:00:00	2025-10-02 20:41:34	["Ruslan R.", "tmbmax", "helga_r80@icloud.com", "Хтось", "Yuliia P", "Karyna", "Кирило", "Віталій"]	[]	{}	
68	Бадмінтон	2025-10-03 10:00:00	2025-10-03 10:14:41	["Кирило", "Dmamp", "Ilona", "Yuliia P"]	[]	{}	
69	Теніс	2025-10-03 18:00:00	2025-10-03 18:02:59	["tmbmax", "Хтось", "Кирило", "Ilona"]	[]	{}	
70	Бадмінтон	2025-10-05 16:00:00	2025-10-05 16:04:25	["Ruslan R.", "tmbmax", "helga_r80@icloud.com", "Karyna"]	["Наталія Овсієнко "]	{}	
71	Бадмінтон  	2025-10-06 19:00:00	2025-10-06 19:04:46	["Наталія Овсієнко ", "Karyna", "tmbmax"]	["Olena A"]	{}	
72	Бадмінтон  	2025-10-07 19:00:00	2025-10-07 19:22:14	["Ilona", "Світлана", "Jeff", "helga_r80@icloud.com"]	["Кирило", "Olha D", "tmbmax"]	{}	
73	Бадмінтон  	2025-10-08 19:00:00	2025-10-08 20:03:02	["Наталія Овсієнко ", "Karyna", "Anna", "Світлана", "Jeff", "Хтось", "tmbmax", "Olena A"]	["Maria"]	{"Грає в інший день": ["tmbmax"]}	
74	Бадмінтон  	2025-10-09 19:00:00	2025-10-09 19:09:45	["Кирило", "bakumvv@gmail.com", "Karyna", "Віталій", "helga_r80@icloud.com", "Anna", "tmbmax", "Olha D"]	["Yuliia P"]	{"Грає в інший день": ["Karyna"]}	
75	Бадмінтон  	2025-10-10 10:00:00	2025-10-10 10:21:26	["Кирило", "Yuliia P", "bakumvv@gmail.com", "Dmamp"]	[]	{}	
76	Теніс	2025-10-10 18:00:00	2025-10-10 18:14:01	["tmbmax", "nadiiab"]	["Кирило"]	{}	
77	Бадмінтон  	2025-10-12 16:00:00	2025-10-12 16:06:05	["Karyna", "Olha D", "Наталія Овсієнко ", "Ruslan R."]	["tmbmax"]	{}	
117	Бадмінтон	2025-10-13 19:00:00	2025-10-13 22:44:06	["Наталія Овсієнко ", "tmbmax", "Olena A", "Karyna"]	[]	{}	
118	Бадмінтон	2025-10-14 19:00:00	2025-10-14 19:05:26	["Наталія Овсієнко ", "tmbmax", "Olena A", "Karyna", "Кирило", "Jeff", "Ruslan R.", "Світлана"]	[]	{}	
119	Бадмінтон	2025-10-15 19:00:00	2025-10-15 19:45:56	["Наталія Овсієнко ", "Karyna", "Laluhovy", "Jeff"]	["tmbmax", "Olena A"]	{}	
120	Бадмінтон	2025-10-16 19:00:00	2025-10-16 19:12:11	["Maria"]	["tmbmax", "Віталій", "sokraticus"]	{}	
121	Бадмінтон	2025-10-16 19:00:00	2025-10-16 19:12:11	["Yuliia P", "Olha D", "Хтось", "Ilona", "Віталій", "tmbmax", "Karyna"]	["Olena A", "Laluhovy"]	{}	
122	Бадмінтон	2025-10-17 10:00:00	2025-10-17 10:04:50	["Karyna", "Кирило", "Ilona", "Olena A"]	["Dmamp"]	{}	
123	Бадмінтон	2025-10-19 16:00:00	2025-10-19 16:13:19	[]	["Ruslan R.", "tmbmax"]	{}	На цей день корт не резервували, тому що не було бажаючих
124	Бадмінтон	2025-10-20 19:00:00	2025-10-20 19:39:16	["Віталій", "Olena A", "Karyna", "tmbmax"]	[]	{}	
125	Бадмінтон	2025-10-21 19:00:00	2025-10-21 19:13:36	["Karyna", "Jeff", "Світлана", "tmbmax"]	["Olena A"]	{}	
126	Бадмінтон	2025-10-22 19:00:00	2025-10-22 19:13:31	["Віталій", "Olena A", "Хтось", "Anna"]	[]	{}	
127	Бадмінтон	2025-10-23 19:00:00	2025-10-23 19:32:17	["Olha D", "helga_r80@icloud.com", "Jeff", "Світлана"]	["tmbmax", "Віталій", "Olena A", "Наталія Овсієнко "]	{}	
128	Бадмінтон	2025-10-24 10:00:00	2025-10-24 11:06:56	["Кирило", "Ilona", "Nastya"]	["Наталія Овсієнко "]	{}	
129	Бадмінтон	2025-10-27 19:00:00	2025-10-27 19:17:19	["Наталія Овсієнко ", "tmbmax", "Світлана", "Jeff"]	["Karyna", "Кирило"]	{}	
130	Бадмінтон	2025-10-28 19:00:00	2025-10-28 19:17:30	["Наталія Овсієнко ", "Karyna", "helga_r80@icloud.com", "Ruslan R.", "tmbmax", "Кирило", "Jeff", "Світлана"]	["Olha D", "Olena A"]	{}	
131	Бадмінтон	2025-10-29 19:00:00	2025-10-29 22:29:03	[]	["Наталія Овсієнко ", "Karyna", "tmbmax", "Olena A", "Jeff", "Світлана", "Anna", "Віталій"]	{}	‼️Друзі! Зміни в розкладі! ‼️\r\n\r\nВ середу регулярна гра відміняється‼️\r\n\r\nВ цей день ми  проводимо  один з етапів змагань.\r\n\r\nУчасники змагань - будь ласка, приходьте на 19:40!
132	Бадмінтон	2025-10-31 10:00:00	2025-10-31 11:35:43	["Karyna", "Dmamp", "Nastya", "HotaMesaros", "Yuliia P", "Кирило", "tmbmax", "Jeff"]	["Olha D", "helga_r80@icloud.com", "Ruslan R."]	{}	
133	Бадмінтон	2025-11-03 20:00:00	2025-11-03 21:29:13	["Karyna", "Наталія Овсієнко ", "tmbmax", "Olha D"]	["Olena A"]	{}	
134	Бадмінтон	2025-11-04 19:00:00	2025-11-04 19:08:32	["Karyna", "tmbmax", "Maria", "Olena A"]	[]	{}	
135	Бадмінтон	2025-11-05 19:00:00	2025-11-05 19:02:05	["Olena A", "Karyna", "Наталія Овсієнко ", "Хтось", "Maria", "Uliana", "Віталій"]	[]	{}	
136	Бадмінтон  	2025-11-06 20:00:00	2025-11-06 20:01:56	["Yuliia P", "Віталій", "tmbmax", "bakumvv@gmail.com", "Olha D", "Кирило", "helga_r80@icloud.com", "Ruslan R."]	["Karyna", "Dmamp"]	{}	В четверг играем в 20:00‼️
137	Бадмінтон	2025-11-07 10:00:00	2025-11-07 15:05:28	["Yuliia P", "Кирило"]	["Dmamp", "HotaMesaros", "Nastya"]	{}	
138	Бадмінтон	2025-11-10 19:00:00	2025-11-10 19:17:34	["Наталія Овсієнко ", "Uliana", "Karyna", "tmbmax"]	[]	{}	
139	Бадмінтон	2025-11-11 19:00:00	2025-11-11 19:00:38	["Ruslan R.", "Jeff", "Світлана", "helga_r80@icloud.com", "Karyna", "Maria", "tmbmax", "Віталій"]	[]	{}	
140	Бадмінтон	2025-11-12 19:00:00	2025-11-12 20:24:37	["Наталія Овсієнко ", "Світлана", "Jeff", "Uliana", "Karyna", "Maria", "tmbmax"]	["Хтось"]	{}	
141	Бадмінтон  	2025-11-13 20:00:00	2025-11-13 20:07:38	["Yuliia P", "Хтось", "Olha D", "bakumvv@gmail.com", "Кирило", "Віталій", "Yuliia Isaieva", "Dmitry"]	["helga_r80@icloud.com", "tmbmax"]	{}	В четвер граємо о 20:00‼️
142	Бадмінтон	2025-11-14 10:00:00	2025-11-14 10:27:24	["Dmamp", "HotaMesaros", "Jeff", "Nastya"]	[]	{}	
\.


--
-- Data for Name: poll; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.poll (id, question, options_json, voted_users_json, date, author) FROM stdin;
2	До вересня в будні дні для мене було б зручно грати у	[{"text": "18:00", "votes": 3}, {"text": "19:00", "votes": 8}]	["Наталія Овсієнко ", "Olena A", "Ilona", "Кирило", "Karyna", "Ruslan R.", "Olga Mc", "helga_r80@icloud.com", "tmbmax"]	2025-07-20 17:00:06	Кирило
1	В які дні краще грати в волейбол?	[{"text": "Вівторок", "votes": 0}, {"text": "Субота", "votes": 5}]	["Vitalij", "Наталія Овсієнко ", "Кирило", "tmbmax", "Laluhovy"]	2025-07-03 06:25:17	Кирило
\.


--
-- Data for Name: removed_participant_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.removed_participant_log (id, removed_user_id, event_id, admin_id, reason, "timestamp") FROM stdin;
42	50	126	2	Перенесено на інший день	2025-11-14 19:58:26.246572
43	52	126	2	Перенесено на інший день	2025-11-14 19:58:31.706291
44	52	124	2	Перенесено на інший день	2025-11-14 19:59:53.858903
45	50	124	2	Перенесено на інший день	2025-11-14 19:59:58.911428
46	53	124	2	Перенесено на інший день	2025-11-14 20:40:51.913106
47	53	126	2	Перенесено на інший день	2025-11-14 20:41:02.609214
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."user" (id, username, password_hash, role, email, email_confirmed, email_confirmation_token, nickname, seen_items_json) FROM stdin;
10	Vitalij	scrypt:32768:8:1$E6KmbaE22uZIHs8L$2776c5270e9f40ca14619af07530dacfa6045bc6404c2f8cd4d4a37d0e27018488e5e239c316f165c7985c90825844df3aa21a397aecc466a86eeae91e0df700	user	ksusairbe@icloud.com	t	\N	\N	{"polls": [1, 2], "announcements": [1]}
5	Olena A	scrypt:32768:8:1$TbeI9QfHAEFV5ttB$50635a4a53932b14afaff363cf29b278bbe7b1246c5a685b8c28e8abbf37aef9e1933a557174e67528ea51ee13eb3503e0ea4277c5ed9eee9626c94583fbbf1d	user	verona.olenka@gmail.com	t	\N	\N	{"announcements": [1, 3], "polls": [1, 2]}
26	tmbmax	scrypt:32768:8:1$9i8RB9xSaMGzIfIF$08c1786db4e89874c53905a348a7362ce8b2e6c3d04630718015d31eb882a02634a6cb5a3cca3b035d2b1917442adb03bcbeac6bec129612aa5caae002228bc7	user	tmbmax@yahoo.co.uk	t	\N	Tanya MB	{"announcements": [1, 3, 4, 5, 6], "polls": [1, 2]}
31	Dmamp	scrypt:32768:8:1$2s3ISI9IbRdPI4h4$c509b598306a54c1c8a1dfa72aed2ef3ebcd34c3c82962572338914d309df591a3af0d6776e827b3d8ac692d0733474143a61d004efc3e75ab292237c51b5f2f	user	ampilogovd@gmail.com	t	\N	Dima	{"announcements": [1, 3, 4, 5, 6, 7, 8, 9], "polls": [1, 2]}
8	Nadiia Johnson	scrypt:32768:8:1$hoL1d9kHnUluwIhy$b92287cd3bcc7d5b73c1fa7f6494a8095ec40568f7740478b1c0c1d795d36d6a0a1f48935a90ef0b37def9d68070c90d014b7864bf6b7e60fbcc1010f06be921	user	johnsonnadiia@gmail.com	t	\N	\N	\N
19	Gedeon347	scrypt:32768:8:1$AMMKFNUfFSIEPLfj$cbcfe53d4ecfdbab1eac2b97fa819a40ea8493962ff7db05da5fbd2410d8d8420de81721b847ab09f21cb30bbe42a28b3ea6a2ceeea015985bb584e6d84a75d7	user	gedeon347140390@gmail.com	t	\N	Сергій	\N
18	Oleksandra 	scrypt:32768:8:1$hZ6OydgrBKUQ5aik$e26edcb7927b85fe8018190def263f7ab5543c6c55c8443d4585b9283249c9b26999dfe6cbbeaa57e013729abb4b30d8277296d8a95e06609eda03d00eb497a7	user	Sashashylina@gmail.com	t	\N	\N	\N
15	Lesia	scrypt:32768:8:1$xgzAJalRz9fSGCfg$c1e75f111bd14bab265bfb16863c485ab06104352cc9a4da9742d649a552331b8bb285add0be8fa2b988cb6f8bf6d9cad0b28ed2f111d90b8b996167a6cbe8e1	user	lisenya03@gmail.com	t	\N	\N	\N
11	Karyna	scrypt:32768:8:1$VVKQlaIXAajj0qUO$0f7beb81378f4d8394093ee44af09a5e782614f6441d9b08747dcc47dc374cc8a5dbbfd489c2168934cbd670e2e38eea1276a52d709f0fd588e8feb438389120	user	karynabakumenko@gmail.com	t	\N	\N	{"announcements": [1], "polls": [1, 2]}
3	Anna	scrypt:32768:8:1$h2d7ZPVccXYor9DI$94550fbacf2b0f4361ee4dcb7f9e54badf82f64cd0b8a237fa9c004016bb5dbcddc1dcc947ba47294e63b22c5adf939bc1548884598822fec68dc8cadb7274ed	user	dubtschak@ukr.net	t	\N	\N	{"announcements": [1, 3, 4, 5, 6, 7, 8, 9]}
16	Ruslan R.	scrypt:32768:8:1$qxhzz0InwVoRv4o5$a9a126639f0838423fcd6cd01c4fe4d0516238dae38def246fa102107de15638116b560eb5fe9a8c81c19f83208f325e99dba0977565608a7270edf6ea9fc6c3	user	razovyrm@gmail.com	t	\N	\N	{"announcements": [1, 3], "polls": [1, 2]}
7	Olga Mc	scrypt:32768:8:1$zso5wXBkVk4MERdq$aaea6990c036ec4923c29d80daae003f1e6dbd8eac0efe174ac2faec360db98d7c3c5ca8423851675066ba71ed177c1b8a194b5bdb39e39535bcc4e768c08fe1	user	olga.mcmahon@gmail.com	t	\N	\N	{"announcements": [1, 3, 4, 5, 6, 7, 8], "polls": [1, 2]}
28	tatiana.shechkova@gmail.com	scrypt:32768:8:1$5xL1kqAU5QRfFP6p$e52cb06e61adf384f3affca0c509390288379b583104af5563bafee59e0f892cf7dfb15bb30bf185e04d38b179de803d0278939cbbf5c2c95b5ee869ed2ca0d6	user	tatiana.shechkova@gmail.com	t	\N	Tatianka	{}
21	Jeff	scrypt:32768:8:1$bp1Mwcn066Q2SkSA$374ac54da6c2d5e6b64d4898b0d1e2a781e53e718cf1c553f9589026dcff075d0b573e13022e1b375f948e7c887d2ecd8ea49c9a6ca759bfdaf805f969b7b5d9	user	jeffreydavidsmith@hotmail.com	t	\N	\N	\N
27	Natali	scrypt:32768:8:1$NgxjwUAwQQ7NrPEc$deb7698dd5199e6e4dc9ffcc8b13a12f00a3971a7e32380a0769d7c72a6563496f9815e5e6652a098657c59be3e1bcd68fc3595767b74cda059b89a22ab88fe9	user	natali_g80@ukr.net	t	\N	Tusia	{}
29	Віталій	scrypt:32768:8:1$ltZaZ5xFpDpDJC6R$2db7e0f1798cf9d1bf657642d5537d82259670e972f5c30804f2ca0555ca8840a36bba4f5b6a38bb0930dd27d28037f70dc75b957bffa7a8cace20f9c3e4b0c1	user	vitalijirbe@icloud.com	t	\N	Vitaly	{"announcements": [1, 3, 4, 5, 6]}
23	Ilona	scrypt:32768:8:1$D7FmJ40D1aVoXzgM$5221961a11b8fa8db79e989f3e408f74c8e917c65800b3d46bae694b1ac7ea0d0540e66513905c63a86a1223bad15ac14e0f510ffca2aad8af4b388081cb8920	user	5159043@gmail.com	t	\N	\N	{"announcements": [1, 3, 4, 5, 6], "polls": [1, 2]}
13	Хтось	scrypt:32768:8:1$tsRFNNfFyOmcqUKK$7b1bb1fc2a945c2545554c4232f7fabf87635ab21585e9dd6751251ae8e60770646292c32c63624d1683522a6c584d3a0c406d3edf1fd8901cdde46bed90c467	user	nazaretto@gmail.com	t	\N	Назаріус	{"polls": [1, 2], "announcements": [1, 3, 4, 5, 6, 7, 8, 9]}
12	Наталія Овсієнко 	scrypt:32768:8:1$uXUjbN5hCZTheHGP$fae28e27292f885d91d0c918d6cd4e2a6abd006701daabf273621f6132e2e4104dd7db99a92870d37df5f87628954392926ad3992158d26b7e126d2b9db550e3	user	ovsienkonatasha@gmail.com	t	\N	Наталі	{"polls": [1, 2], "announcements": [1, 3, 4, 5, 6, 7, 8, 9, 10]}
14	helga_r80@icloud.com	scrypt:32768:8:1$g0YL5WsDMCULut51$d83ce91d1487c3dfed6639850217c45bca39ca46e477b33bf35db539862af7785958231a93239a238590b02327363b463c394bd4770dae2db231b68c87638817	user	helga_r80@icloud.com	t	\N	Оля Р	{"announcements": [1, 3, 4, 5, 6, 7, 8, 9, 10], "polls": [1, 2]}
20	Світлана	scrypt:32768:8:1$Zkg2Z8DN8e4ENw3a$fe3037cc0a3bc0e14ee710b6b8bfba89d9dcba19b1d127a10bca5d6b36e501fdd42803f60eff67c7e5cc992786714a5c0eb742c358b7292e3263cd1c12fde083	user	Spkonon8@gmail.com	t	\N	\N	{"announcements": [1, 3, 4, 5, 6, 7, 8], "polls": [1, 2]}
30	bakumvv@gmail.com	scrypt:32768:8:1$oU5TqovqUpZF5rci$b33606b4ef058a205b2c601060e87b786691f9231752f67b6bf4b603e9d420be3a591b1d8725f78eb1eb4a50e1ffbe3467a5c9fde7aab777e16fc988bddb416d	user	bakumvv@gmail.com	t	\N	Viktor	{}
2	Кирило	scrypt:32768:8:1$P6iR51Su8mIPQxXJ$e145ed56f623b834633aec1a0492a2d084714b6ae8bfd5e8c2565afb4980e3e7f8901c8c4061c98df004ff55b55c1a6895e98487f60cead18f73d52c90bab4be	admin	kirill.grig.2000@gmail.com	t	\N	\N	{"polls": [1, 2], "announcements": [1, 3, 4, 5, 6, 7, 8, 9, 10]}
22	Denys	scrypt:32768:8:1$hevag4RvmWFZBaDJ$3ffcff6a56970fa7913e059f390c3fd0b8d922adb17b1974ec6c6f3b57e5e2d62e0f8e6851a8d4b6b398bcda5c0b02ebc9721fa1cbde3e04909bc8dcf0a61db4	user	kobets2402@gmail.com	t	\N	\N	\N
9	Olha D	scrypt:32768:8:1$sOqIKGmREvXB9rof$654785582ad14eeb754f3e3765eae30d875679767f93588816dac0e4734fb82863181645b481c8ee1fd533d71a3b65bfb4c06deeffa80d982266593874475a91	user	olyader49@gmail.com	t	\N	\N	{"polls": [1, 2], "announcements": [1, 3, 4, 5, 6, 7, 8]}
41	odessitka88@ukr.net	scrypt:32768:8:1$GmbSs5pGxY0uHa0e$4b86e8bda32f93fc4486cafc5c450d809974ecaa1f863f0cb83db548d1a97ab5bddd88e5bc4c37aa19a116f110fd9b7b24f4ae80c20333e858cb9a3c24db89d6	user	odessitka88@ukr.net	t	\N	Uliana	{}
42	Uliana	scrypt:32768:8:1$DetVoBMp8tcegx0B$b46a56187e32e1c9ed50705fa4e12245a39d9a7a31540a0bbb12e3d361f5971d15e7a9e1e023477cf8b00079f55fe9a749674282e95a8c863becadc19da7473a	user	udovichenkouliana@icloud.com	t	\N	Uliana	{}
40	HotaMesaros	scrypt:32768:8:1$mvVk9BcWHXRLXMIh$d5becd6be0989a2a484d3350a46453ccc8041a10f5f62baf0a7d2140e9abd5e925658978303ad2d59bf5d8b7fa827ccb5d3298fbe996e1aaf8b8fda695d263cc	user	stakhovanatali@gmail.com	t	\N	Nataliia	{"polls": [1, 2]}
33	George	scrypt:32768:8:1$91bGk1A4L66DMKbZ$4f16744e86de8e75e4bea28bcbc4f1896dfe014399d03815c8c8a3dea9dad43a2371dbd509509e444d0ae3a40a1a4fdbf606fa95a81eb622aba4c2aa3ee869e7	user	vanilakanfetk@gmail.com	t	\N	George	{"announcements": [1, 3, 4, 5, 6]}
43	Alinakeeley88@gmail.com	scrypt:32768:8:1$wjE2A8C7OZZ8oUfv$fefa45de8c64884879a86c803f0ff4f23692759ff63a0091b535c90d476f133223f11d4898f2eccacd6f73c96d35a778f2735d3ee72268f8d171efcfb3878f71	user	Alinakeeley88@gmail.com	t	\N	Alina	{}
44	Alina	scrypt:32768:8:1$odp50tVGzskvhkDV$1b52d87ab888e00314306776b2399cf95d7bcf32852a2aba5c801b3d87b9acd0d735bf3137d19de992555e1652f3eaca18fd72f357537ed4ad16a51e58564ef8	user	Alinochka2s4u@gmail.com	t	\N	Alina	{}
34	sokraticus	scrypt:32768:8:1$7T5E75pLiUYUWHyM$8062497b1ac6b31435498ec97253f54100358f9f8256a4a675b81e2e88f07b60f95d11a23b574952c9a52ae3d36d96a7368547e24e84559aedd344db239e2ed6	user	kuznietsov.yaroslav@gmail.com	t	\N	Ярослав Кузнєцов	{"announcements": [1, 3, 4, 5, 6], "polls": [1, 2]}
45	Yuliia	scrypt:32768:8:1$fF1Axnk06UV4Xm78$6fc3b4333ea46c38b4a3699255e26f7f39ccd15bb150658f56c52f43ef496d5b96d4efc7b26fe5c2809e1891d57bcdb86f13891d4be6fedff7f250ac39673cae	user	isayeva.jn@gmail.com	t	\N	Yuliia_ne trener	{}
32	Maria	scrypt:32768:8:1$FChsZBrvuRzOLDfO$edf688a882d932695cf4b0171b0e9718cd354846ed710151de5f3c75b90a9e3ff72510ca7eaaa1b5c96885d61a9dac087f665734c560e16ae7072fd21af78304	user	tatadzemaria@gmail.com	t	\N	MariaT	{}
36	nadiiab	scrypt:32768:8:1$VVJvOiUqf8Ai36k2$bd9474b756cdb866d8acf42b42c5d015a5aead8d7fb8ad4d9808b4b2814073c1fe242827d2076715e6da859cc0ae457c8e556b08cd08db2c40a9decb9c59b3b0	user	nada.shanya@gmail.com	t	\N	Nadiia	{}
47	Mariya	scrypt:32768:8:1$HEA5sVhrrR7M36n2$d2223cff6bd417c0205befde0e6c506aaee9dcae4784b9363c8feba27623d215e50c973824a5f3df7373721e83761690315d88c79423c5f50ae38535ae1dc8c6	user	mariyahirnaya@icloud.com	t	\N	Mariya	{}
48	Dmitry	scrypt:32768:8:1$w0FAiLPpnN9yEf48$6bfc561734bcf9176fddd42d1aa102d90b18884fa7eb64b9ccbe73b5549c545b8f4e11db5cf51430148d08617f2022379c511f455cabba737727f6dc571ee3ce	user	udaff.on.air@gmail.com	t	\N	Dmitry	{}
35	Laluhovy	scrypt:32768:8:1$XbYTFBfBfNHpQhUQ$3c92b0920709746fd25306440fa3f2d439a283b1bcf4b7151757deaa8a39b1261972015c7da70ffb9ad3c166f4bdd80a23f2c8b25556faed11f901c7cdd7db0e	user	oleksiiluhovyi@gmail.com	t	\N	Олексій	{"announcements": [1, 3, 4, 5, 6, 7, 8], "polls": [1, 2]}
17	Yuliia P	scrypt:32768:8:1$72i83cATnERWrh8P$9ad67cf043e12e598696691eb0b8edad398ebf22048f5c7e23e90388acb4f1667f95e5b9b3570931007766bb12800e7946fcc7c49ab62af39e0aa0ea1576eeb1	user	efimiyanos@gmail.com	t	\N	брЮлік	{"polls": [1, 2], "announcements": [1, 3, 4, 5, 6, 7, 8, 9]}
37	Nastya	scrypt:32768:8:1$isQBhotYWfLCTHvo$d3e206fdb74f4e8c2ae56f4312289d01219d82d23974d223e179b41c43f05a6a8d08cccc9fdee2d76253ccdab163944c1c1d6d3311b085702e36acdf11a17b0a	user	suroksuslyak@gmail.com	f	f4a31ddff2e338c9fe9b331d4a3aa913cc18797432c5cd17	Nastya	{}
38	NastySilchenko	scrypt:32768:8:1$Rd5QxwqwavkRykWR$8c1aeb8abfd609721ac2b0809aae9cd1a1c514686826234d8583a0765f8d5a33404b0b8cb4bad461daf3d31c60505e0b3c7b16d0d2679261c5dfdd656297a882	user	kikkir@icloud.com	f	de940f74d589f09cd531cd03b0b1bf6eff77f6bc68fd7bed	Nastya	{}
46	Yuliia Isaieva	scrypt:32768:8:1$EbzNhqdzoQOC0jjO$9a6ac2fd2e7dc9c00530b629b619cf1eacf7f3438bf2bf2082cd05ee5de3eea1b47f4eae0ba725dfeab7f03ec9277b360ad8ba9e564a65d697389b85ffe1e509	user	lourdes@ukr.net	t	\N	Yuliia_ne trener	{"announcements": [1, 3, 4, 5, 6, 7, 8, 9, 10], "polls": [1, 2]}
49	Alina Keeley	scrypt:32768:8:1$vOZlI3CB3JYOhkhB$8e2a384bd0641eb343df360b6f8ef843af60b9ddc2da84ecffa2a50a8d45854eb2001f0f7b854571c3dae75efc998a7a9986bb9bc799900b40b485cf16f5ca24	user	Zatokovenkot@gmail.com	t	\N	zAlina	{}
50	Krasivaya	scrypt:32768:8:1$CZdSD3tBqs4zgks2$9d1c1e7f4d05c373594ac81325bd44fee1f9f4dab7c47f8ee17d29c372ac1091cd75671cfc3157172d5452a2cbd871bbde67eaee97264d8048a9acb33d1a9fb6	user	blabla987@mailforspam.com	t	\N	Красивая	{}
51	Maria123	scrypt:32768:8:1$uSuFjsfMs3TOnsWi$7d28116d9ea978d9b6b7f32b16ecbbd3dc3bc49cb86794e7100577b9116cde2a1956ebda1fbc0cfb591f3d8b2692b0fc022bc4b7a01a425c08fc91df4d1cdec0	user	maria@maria.com	t	\N	Марія	{}
52	Jozefina	scrypt:32768:8:1$ijq4AVxf3lOtfbtR$9c4bf3c820005ab7b6197526ebaff12a37fdcd730e11fab93ffb3ea099d75ff74eede7e243790f321701b384796ec4254566013e286bcdaa3968df050d541d68	user	jozefina@gmail.com	t	\N	Jozefina	{}
53	Mona	scrypt:32768:8:1$ifltNAxwYC68bEub$19443f491238b7a7778685ec9f1efd0069f9c0c33305183e32c75c22aff5d6509499ee3f36c9177d1013a0f830f81dcb8baae07f2cbb957bafda28691bfdc953	user	mona@gmail.com	t	\N	Mona Lisa	{}
56	Кирило2	scrypt:32768:8:1$ByZBlhvsr1eeP4Wq$cfb4c21651842ccafc0ec1a347610b929deeec0fba5317d8873dd6500f8db5f0a40def5ac5ad68d3d93c74cb621f5a821d266a1b2c6f1b8adbc40e238e870167	user	kirg2017@ukr.net	f	aad9805751007e373e677f0fc5e32d6bfde038a2b9a65a97	Кирило2	{}
\.


--
-- Name: announcement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.announcement_id_seq', 10, true);


--
-- Name: event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_id_seq', 126, true);


--
-- Name: event_participant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_participant_id_seq', 223, true);


--
-- Name: financial_transaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.financial_transaction_id_seq', 97, true);


--
-- Name: game_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.game_log_id_seq', 142, true);


--
-- Name: poll_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.poll_id_seq', 2, true);


--
-- Name: removed_participant_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.removed_participant_log_id_seq', 47, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_id_seq', 56, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: announcement announcement_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcement
    ADD CONSTRAINT announcement_pkey PRIMARY KEY (id);


--
-- Name: event_participant event_participant_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_participant
    ADD CONSTRAINT event_participant_pkey PRIMARY KEY (id);


--
-- Name: event event_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_pkey PRIMARY KEY (id);


--
-- Name: financial_transaction financial_transaction_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.financial_transaction
    ADD CONSTRAINT financial_transaction_pkey PRIMARY KEY (id);


--
-- Name: game_log game_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.game_log
    ADD CONSTRAINT game_log_pkey PRIMARY KEY (id);


--
-- Name: poll poll_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.poll
    ADD CONSTRAINT poll_pkey PRIMARY KEY (id);


--
-- Name: removed_participant_log removed_participant_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.removed_participant_log
    ADD CONSTRAINT removed_participant_log_pkey PRIMARY KEY (id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user user_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- Name: event_participant event_participant_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_participant
    ADD CONSTRAINT event_participant_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.event(id) ON DELETE CASCADE;


--
-- Name: event_participant event_participant_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_participant
    ADD CONSTRAINT event_participant_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: removed_participant_log removed_participant_log_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.removed_participant_log
    ADD CONSTRAINT removed_participant_log_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: removed_participant_log removed_participant_log_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.removed_participant_log
    ADD CONSTRAINT removed_participant_log_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.event(id) ON DELETE CASCADE;


--
-- Name: removed_participant_log removed_participant_log_removed_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.removed_participant_log
    ADD CONSTRAINT removed_participant_log_removed_user_id_fkey FOREIGN KEY (removed_user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

