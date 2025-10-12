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
    participants_json text,
    teams_json text,
    comment text
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
-- Name: financial_transaction; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.financial_transaction (
    id integer NOT NULL,
    description character varying(255) NOT NULL,
    date character varying(10) NOT NULL,
    amount double precision NOT NULL,
    transaction_type character varying(20) NOT NULL,
    logged_by_admin character varying(80) NOT NULL,
    logged_at character varying(20)
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
    event_date character varying(20) NOT NULL,
    logged_at character varying(20),
    active_participants_json text,
    cancelled_participants_json text,
    teams_json text,
    image_url character varying(255),
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
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    password_hash character varying(256) NOT NULL,
    role character varying(20),
    has_paid_fees boolean,
    last_fee_payment_date character varying(10),
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
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
03c0ee0bfd31
\.


--
-- Data for Name: announcement; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.announcement (id, title, content, date, author) FROM stdin;
9	ПРАВИЛА	Правила прості. Ніхто нікого ні до чого не примушує. Ми створюємо простір, де можемо поспілкуватись, разом активно провести час. Кожен може запропонувати ідею і знайти однодумців.\r\n\r\nМи проводили пікніки, катались на велосипедах, на сапах, грали у волейбол, бадмінтон, теніс, пінг-понг, піклбол. Далі - буде...\r\n\r\nЯк стати учасником - досить просто. Зв'язатись з адміністраторами https://chat.whatsapp.com/HEdv3OLrTS6IDw7It8Rf7x\r\n\r\nДля того, щоб ми могли грати у приміщенні, закупляти призи на замагання, організовувати активності і закупляти інвентар - нам потрібні гроші. Фінансовий звіт ми викладаємо тут кожного місяця. Тому учасники клубу сплачують 10 ф. на місяць. А організатори, зі свого боку, майже стовідсотково нададуть вам змогу пограти хоча б раз на тиждень у закритому приміщенні (а також - тенісний корт). На жаль, на зараз наші можливості обмежені двома кортами на день максимум.\r\n\r\nЯк дізнатись коли і з ким можна пограти.\r\nДля цього ми зробили додаток, в який додали розклад ігор в найбільш поширений час. \r\nhttps://ua-sport-active-kent.up.railway.app/\r\nЯкщо у вас є побажання провести гру у інший час (не одноразово, а на постійній основі), проведіть опитування (приватно, або в групі) і, якщо знайдеться необхідна кількість учасників - ми додамо цей час в наш розклад.\r\n\r\nЯк правильно записатись на гру. В кінці тижня ми викладаємо розклад на наступний тиждень. Записуйтесь на гру в ті дні, в які ви можете грати (навіть, якщо це буде 6 днів на тиждень). Для організаторів це дає можливість комбінувати склад учасників, враховувати індивідуальні особливості і інші нюанси. Але пам'ятайте, що ви можете грати як 6 днів, якщо будуть вільні місця, так і 1 день - той, який ми точно зможемо організувати. (Ми найближчим часом додамо статистику і організатори зможуть більш рівномірно розподіляти ігри для тих хто грає часто).\r\nЩо ми робимо, коли на гру записалось більше, ніж може грати.\r\n1. Новачок. Для того, хто вперше приходить на знайомство з грою ми надаємо таку перевагу, як комплімент від учасників клубу.\r\n2. Внески. Перевага тим, хто сплатив внесок\r\n3. Кількість ігор на тижні. Перевага тому, хто грав менше\r\n4. Черга. Перевага тому, хто записався раніше.\r\n\r\nМеленький нюанс. Якщо ви зареєструвались і згадали, що в якийсь день не зможете - ви можете відмовитись від гри. Якщо відмовитесь більше ніж через годину після реєстрації, то зі списку ви не зникнете, а навпроти вас буде відповідна помітка.	2025-10-12 19:43:31	Кирило
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

COPY public.event (id, name, date, image_url, participants_json, teams_json, comment) FROM stdin;
80	Бадмінтон	2025-10-15 19:00:00	\N	[{"username": "Наталія Овсієнко ", "timestamp": "2025-10-11 21:55:11", "status": "active"}, {"username": "tmbmax", "timestamp": "2025-10-12 05:03:04", "status": "active"}, {"username": "Olena A", "timestamp": "2025-10-12 07:09:16", "status": "active"}, {"username": "Karyna", "timestamp": "2025-10-12 12:10:38", "status": "active"}, {"username": "Laluhovy", "timestamp": "2025-10-12 15:45:39", "status": "active"}, {"username": "Jeff", "timestamp": "2025-10-12 18:04:03", "status": "active"}]	{}	
79	Бадмінтон	2025-10-14 19:00:00	\N	[{"username": "Наталія Овсієнко ", "timestamp": "2025-10-11 21:55:06", "status": "active"}, {"username": "tmbmax", "timestamp": "2025-10-12 05:02:58", "status": "active"}, {"username": "Olena A", "timestamp": "2025-10-12 07:09:02", "status": "active"}, {"username": "Karyna", "timestamp": "2025-10-12 12:10:21", "status": "active"}, {"username": "Кирило", "timestamp": "2025-10-12 15:27:52", "status": "active"}, {"username": "Jeff", "timestamp": "2025-10-12 18:03:07", "status": "active"}, {"username": "Ruslan R.", "timestamp": "2025-10-12 18:33:22", "status": "active"}]	{}	
81	Бадмінтон	2025-10-16 19:00:00	\N	[{"username": "tmbmax", "timestamp": "2025-10-12 05:03:34", "status": "active"}, {"username": "sokraticus", "timestamp": "2025-10-12 11:53:04", "status": "active"}, {"username": "Laluhovy", "timestamp": "2025-10-12 13:47:44", "status": "cancelled"}, {"username": "Maria", "timestamp": "2025-10-12 14:56:51", "status": "active"}, {"username": "Віталій", "timestamp": "2025-10-12 15:43:04", "status": "active"}]	{}	
82	Бадмінтон	2025-10-16 19:00:00	\N	[{"username": "tmbmax", "timestamp": "2025-10-12 05:03:16", "status": "active"}, {"username": "Olena A", "timestamp": "2025-10-12 07:09:31", "status": "active"}, {"username": "Olha D", "timestamp": "2025-10-12 11:24:12", "status": "active"}, {"username": "Karyna", "timestamp": "2025-10-12 12:11:03", "status": "active"}, {"username": "Хтось", "timestamp": "2025-10-12 13:54:18", "status": "active"}, {"username": "Ilona", "timestamp": "2025-10-12 15:36:58", "status": "active"}, {"username": "Віталій", "timestamp": "2025-10-12 15:44:29", "status": "active"}, {"username": "Laluhovy", "timestamp": "2025-10-12 15:45:21", "status": "active"}]	{}	
84	Бадмінтон	2025-10-19 16:00:00	\N	[{"username": "tmbmax", "timestamp": "2025-10-12 05:03:46", "status": "active"}]	{}	
83	Бадмінтон	2025-10-17 10:00:00	\N	[{"username": "Olena A", "timestamp": "2025-10-12 07:09:55", "status": "active"}, {"username": "Karyna", "timestamp": "2025-10-12 12:11:17", "status": "active"}, {"username": "Кирило", "timestamp": "2025-10-12 15:28:23", "status": "active"}, {"username": "Ilona", "timestamp": "2025-10-12 15:36:08", "status": "active"}, {"username": "Dmamp", "timestamp": "2025-10-12 16:33:49", "status": "active"}]	{}	
78	Бадмінтон	2025-10-13 19:00:00	\N	[{"username": "Наталія Овсієнко ", "timestamp": "2025-10-11 21:55:01", "status": "active"}, {"username": "tmbmax", "timestamp": "2025-10-12 05:02:44", "status": "active"}, {"username": "Olena A", "timestamp": "2025-10-12 07:08:45", "status": "active"}, {"username": "Karyna", "timestamp": "2025-10-12 12:10:05", "status": "active"}]	{}	
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
78	Перекидне табло	2025-10-10	-18	expense	Кирило	2025-10-10 11:35:53
52	Оплата мембершіп Юля	2025-09-06	-40	expense	Кирило	2025-09-07 14:27:01
79	Членський внесок (2025-10) від Olena A	2025-10-10	10	income	Кирило	2025-10-10 15:36:22
\.


--
-- Data for Name: game_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.game_log (id, event_name, event_date, logged_at, active_participants_json, cancelled_participants_json, teams_json, image_url, comment) FROM stdin;
1	Бадминтон	2025-07-03 19:00:00	2025-07-03 20:02:16	["Кирило"]	[]	{"Сонечки": ["Кирило"]}	\N	\N
2	Теніс	2025-07-04 19:00:00	2025-07-04 20:25:26	["Кирило"]	["Anna"]	{"Сонечки": ["Кирило"], "Метелики": []}	\N	\N
3	Волейбол	2025-07-05 17:00:00	2025-07-05 22:20:31	[]	["Кирило"]	{"Сонечки": []}	\N	\N
4	Теніс	2025-07-06 18:00:00	2025-07-06 18:31:41	["Anna", "Nadiia Johnson"]	[]	{}	\N	Граємо разом
5	Бадминтон	2025-07-08 19:00:00	2025-07-08 21:08:53	["Кирило", "Olga Mc", "helga_r80@icloud.com", "Ruslan R.", "Oleksandra ", "Gedeon347"]	[]	{"Метелики": ["Кирило", "Olga Mc", "helga_r80@icloud.com", "Ruslan R."]}	\N	Може бути змінено в залежності від кількості і складу учасників. Обирайте всі можливі варіанти
6	Бадминтон	2025-07-09 19:00:00	2025-07-09 19:17:59	["Anna", "Olha D", "Olena A", "Vitalij", "Хтось", "Yuliia P", "Світлана", "Jeff"]	["Кирило"]	{"Метелики": ["Olha D", "Olena A", "Світлана", "Jeff"], "Крафті": ["Anna", "Vitalij", "Хтось", "Yuliia P"]}	\N	Може бути змінено в залежності від кількості і складу учасників. Обирайте всі можливі варіанти
7	Бадминтон	2025-07-10 19:00:00	2025-07-10 19:30:06	["Кирило", "Vitalij", "Karyna", "Наталія Овсієнко ", "Olha D"]	[]	{}	\N	Може бути змінено в залежності від кількості і складу учасників. Обирайте всі можливі варіанти
8	Теніс	2025-07-11 19:00:00	2025-07-11 20:44:42	["Кирило", "Хтось", "Ruslan R.", "helga_r80@icloud.com", "Olga Mc"]	["Vitalij"]	{}	\N	
9	Волейбол	2025-07-12 17:00:00	2025-07-12 17:29:41	["Кирило", "Vitalij", "Хтось"]	[]	{}	\N	Відміняємо волейбол, бо частина поїхала на лаванду, а в трьох грати не цікаво...
10	Теніс	2025-07-13 18:00:00	2025-07-13 18:04:48	["Nadiia Johnson"]	[]	{}	\N	
11	Бадмінтон	2025-07-15 19:00:00	2025-07-15 19:09:22	["Oleksandra ", "Кирило", "Karyna", "Gedeon347"]	[]	{"Корт 2": ["Oleksandra", "Кирило", "Karyna", "Gedeon347"]}	\N	
12	Бадмінтон	2025-07-16 19:00:00	2025-07-16 20:16:26	["Olha D", "helga_r80@icloud.com", "Ruslan R.", "Vitalij", "Хтось", "Світлана", "Jeff", "Karyna", "Anna", "Olga Mc"]	[]	{"Грає в інший день": ["Vitalij", "Karyna"], "Корт 2": ["Olha D", "Світлана", "Jeff", "Olga Mc"], "Корт 3": ["helga_r80@icloud.com", "Ruslan R.", "Хтось", "Anna"]}	\N	
13	Бадмінтон	2025-07-17 19:00:00	2025-07-17 20:00:30	["Кирило", "Наталія Овсієнко ", "Vitalij", "Karyna"]	[]	{"Корт 1": ["Кирило", "Наталія Овсієнко", "Vitalij", "Karyna"]}	\N	
14	Теніс	2025-07-18 19:00:00	2025-07-18 19:21:13	["Кирило", "Ilona", "Хтось"]	["Olga Mc"]	{}	\N	
15	Волейбол	2025-07-19 17:00:00	2025-07-20 14:48:02	["Кирило", "Наталія Овсієнко "]	[]	{}	\N	Гру відміняємо. Бо після свята Абетки нікого зібрати не можу
16	Теніс	2025-07-20 18:00:00	2025-07-20 18:05:08	["Nadiia Johnson"]	[]	{}	\N	
17	Бадмінтон	2025-07-23 19:00:00	2025-07-23 22:35:28	["Світлана", "Jeff", "Olga Mc", "Anna"]	["Наталія Овсієнко "]	{}	\N	Пройдіть опитування, якщо хочете змінити час гри з 19:00 на 18:00
18	Бадмінтон	2025-07-24 19:00:00	2025-07-24 19:54:35	["Наталія Овсієнко ", "Ilona", "Ruslan R.", "Olena A"]	[]	{}	\N	Пройдіть опитування, якщо хочете змінити час гри з 19:00 на 18:00
19	Теніс	2025-07-25 19:00:00	2025-07-26 22:12:39	["Кирило", "Ruslan R.", "Olha D", "Olga Mc"]	["Ilona"]	{}	\N	Пройдіть опитування, якщо хочете змінити час гри з 19:00 на 18:00
20	Волейбол	2025-07-26 17:00:00	2025-07-26 22:12:39	["Наталія Овсієнко "]	[]	{}	\N	
21	Теніс	2025-07-27 18:00:00	2025-07-27 19:28:54	[]	[]	{}	\N	
22	Бадмінтон	2025-07-24 19:00:00	2025-07-27 20:57:52	[]	[]	{}	\N	
23	Бадмінтон	2025-07-24 19:00:00	2025-07-27 20:58:29	[]	[]	{}	\N	
24	Бадмінтон	2025-07-29 20:00:00	2025-07-29 20:15:03	["Кирило", "Olga Mc", "Ilona", "Anna"]	[]	{}	\N	УВАГА! Зміна часу!!!\r\nНа 17, 18,19 годин корти всі вже зайняті. Тому букаємо корт на 20:00
25	Бадмінтон	2025-07-30 19:00:00	2025-07-30 19:15:39	["Кирило", "Anna", "Olha D", "Olena A"]	[]	{}	\N	
26	Бадмінтон	2025-07-31 19:00:00	2025-07-31 21:41:56	["Karyna", "Світлана", "Jeff"]	["Кирило", "tmbmax"]	{}	\N	
27	Теніс	2025-08-01 19:00:00	2025-08-01 19:27:51	["Кирило", "Olga Mc", "Ilona", "tmbmax"]	["Olha D"]	{}	\N	Ми знову змінили час на 19:00 ))). \r\n\r\n
28	Бадмінтон  	2025-08-05 19:00:00	2025-08-05 19:53:52	["tmbmax", "Jeff", "Karyna", "Кирило", "helga_r80@icloud.com"]	[]	{"Грає в інший день": ["helga_r80@icloud.com"]}	\N	
29	Бадмінтон  	2025-08-06 19:00:00	2025-08-06 19:47:21	["Ilona", "Olena A", "Oleksandra ", "Gedeon347", "Olga Mc", "Jeff", "Karyna", "Anna", "Yuliia P", "Кирило"]	[]	{"Корт 4": ["Oleksandra", "Gedeon347", "Olga Mc"], "Грає в інший день": ["Jeff", "Karyna"], "Корт 5": ["Ilona", "Olena A", "Anna", "Yuliia P"], "замість мене - Вікторія, корт 4": ["Кирило"]}	\N	
30	Бадмінтон  	2025-08-07 19:00:00	2025-08-08 08:03:29	["tmbmax", "Karyna", "helga_r80@icloud.com", "Ruslan R."]	[]	{"Корт 4": ["tmbmax", "Karyna", "helga_r80@icloud.com", "Ruslan R."]}	\N	
31	Теніс	2025-08-08 19:00:00	2025-08-08 21:18:01	["tmbmax", "Olga Mc", "Jeff", "Кирило", "Yuliia P", "Karyna", "Ilona"]	[]	{}	\N	
32	Бадмінтон  	2025-08-12 19:00:00	2025-08-12 19:11:53	["Кирило", "Ilona", "Jeff", "Karyna", "tmbmax", "Olha D"]	["Yuliia P", "Olga Mc"]	{"Корт 2": ["tmbmax", "Olha D", "Ilona", "Кирило", "Jeff"], "Грає в інший день": ["Karyna"]}	\N	
33	Бадмінтон  	2025-08-13 19:00:00	2025-08-14 07:46:01	["Кирило", "Jeff", "helga_r80@icloud.com", "Ruslan R."]	[]	{}	\N	
66	Бадмінтон	2025-10-01 19:00:00	2025-10-01 19:34:34	["tmbmax", "Хтось", "Karyna", "Наталія Овсієнко ", "Світлана", "Jeff", "Anna"]	["Ruslan R.", "Віталій"]	{}	\N	
34	Бадмінтон  	2025-08-14 19:00:00	2025-08-14 20:00:59	["Кирило", "Olga Mc", "Jeff"]	["Ilona"]	{"Грає в інший день": ["Jeff", "Olga Mc", "Кирило"]}	\N	Увага! Ми відміняємо гру в цей день. Перебудуйте ваші плани.
35	Теніс	2025-08-15 19:00:00	2025-08-17 18:03:41	["Yuliia P", "Olga Mc", "Jeff", "tmbmax"]	["Кирило", "Ilona"]	{}	\N	
36	Бадмінтон	2025-08-19 19:00:00	2025-08-19 20:58:59	["tmbmax", "helga_r80@icloud.com", "Ruslan R.", "Olha D", "Ilona", "Світлана", "Jeff", "Кирило"]	[]	{"Грає в інший день": ["helga_r80@icloud.com", "Ruslan R.", "Світлана", "Jeff"], "Корт 3": ["tmbmax", "Olha D", "Ilona", "Кирило"]}	\N	
37	Бадмінтон	2025-08-20 19:00:00	2025-08-20 19:00:06	[]	[]	{}	\N	
38	Бадмінтон	2025-08-21 19:00:00	2025-08-21 21:19:38	["helga_r80@icloud.com", "Ruslan R.", "Світлана", "Jeff"]	[]	{}	\N	
39	Теніс	2025-08-22 19:00:00	2025-08-22 19:43:45	[]	["tmbmax"]	{}	\N	
40	Бадмінтон  	2025-08-26 19:00:00	2025-08-26 19:39:46	["helga_r80@icloud.com", "Olha D", "tmbmax", "Ruslan R.", "Olga Mc"]	[]	{}	\N	
41	Бадмінтон  	2025-08-27 19:00:00	2025-08-27 19:36:53	["Karyna"]	["Світлана"]	{}	\N	
42	Бадмінтон  	2025-08-28 20:00:00	2025-08-29 08:24:56	["helga_r80@icloud.com", "Ruslan R.", "Karyna", "Olha D"]	[]	{}	\N	
43	Теніс	2025-08-29 19:00:00	2025-08-30 17:21:31	["tmbmax", "Хтось", "Ilona"]	["Olga Mc"]	{}	\N	
44	Бадмінтон  	2025-09-02 19:00:00	2025-09-02 19:08:37	["helga_r80@icloud.com", "Ruslan R."]	[]	{"Корт 2": ["Ruslan R.", "helga_r80@icloud.com"]}	\N	
45	Бадмінтон  	2025-09-03 19:00:00	2025-09-04 07:37:26	["Віталій", "Olga Mc", "Хтось", "Anna"]	["Кирило", "helga_r80@icloud.com"]	{"Корт 1": ["Віталій", "Olga Mc", "Хтось", "Anna"]}	\N	
46	Бадмінтон  	2025-09-04 19:00:00	2025-09-04 20:06:57	["Кирило", "Віталій", "Karyna", "Наталія Овсієнко "]	[]	{"Корт 4": ["Наталія Овсієнко", "Karyna", "Віталій", "Кирило"]}	\N	
47	Теніс	2025-09-05 19:00:00	2025-09-05 19:12:35	["Кирило", "Olga Mc", "Хтось", "tmbmax"]	[]	{}	\N	
48	Бадмінтон	2025-09-09 19:00:00	2025-09-09 19:07:40	["Кирило", "helga_r80@icloud.com", "Olga Mc", "Ruslan R."]	["Віталій"]	{}	\N	
49	Бадмінтон	2025-09-10 19:00:00	2025-09-10 19:13:01	["Кирило", "Karyna", "Віталій", "Anna", "Хтось"]	["Наталія Овсієнко "]	{"Грає в інший день": ["Кирило"]}	\N	Друзі, час - 19:00!!!\r\nБуває, що коли вношу гру, можу не додивитись час. Час у нас поки що один - 19:00. Окрім гри на вулиці - там 18:00.\r\nЯкщо бачите, що час відрізняється - повідомте мені, я виправлю.\r\n
50	Бадмінтон	2025-09-11 19:00:00	2025-09-11 19:03:23	["Ilona", "Кирило", "tmbmax", "helga_r80@icloud.com", "Наталія Овсієнко "]	[]	{"Грає в інший день": ["Кирило"]}	\N	
51	Теніс	2025-09-12 18:00:00	2025-09-12 18:48:05	["Кирило", "Хтось", "tmbmax"]	[]	{}	\N	ВІДМІНА !!!\r\n\r\nЗ погодних умов відміняємо гру.Сильний вітер
52	Бадмінтон	2025-09-15 19:00:00	2025-09-15 20:17:59	[]	["Ilona"]	{}	https://sportano.ua/blog/wp-content/uploads/2024/01/Badminton-zasady-gry.jpg	
53	Бадмінтон	2025-09-16 19:00:00	2025-09-16 19:26:38	["Кирило", "helga_r80@icloud.com", "Наталія Овсієнко ", "Ruslan R.", "tmbmax"]	[]	{"Грає в інший день": ["Кирило"]}	https://sportano.ua/blog/wp-content/uploads/2024/01/Badminton-zasady-gry.jpg	
54	Бадмінтон	2025-09-17 19:00:00	2025-09-17 19:01:23	["Віталій", "Кирило", "Наталія Овсієнко ", "Anna", "Хтось", "Karyna", "Ilona"]	["Olha D", "helga_r80@icloud.com"]	{}	https://sportano.ua/blog/wp-content/uploads/2024/01/Badminton-zasady-gry.jpg	
55	Бадмінтон	2025-09-18 19:00:00	2025-09-18 20:38:38	["Віталій", "Кирило", "Karyna", "bakumvv@gmail.com", "Yuliia P", "Olha D", "helga_r80@icloud.com", "tmbmax", "Anna"]	["Наталія Овсієнко "]	{"Грає в інший день": ["Наталія Овсієнко", "Anna"]}	https://sportano.ua/blog/wp-content/uploads/2024/01/Badminton-zasady-gry.jpg	Наталі грає в інший день.
56	Теніс	2025-09-19 18:00:00	2025-09-20 10:54:35	["Кирило", "Olga Mc"]	["Ilona"]	{}	https://extremstyle.ua/storage/user_1/images%201/kak-vybrat-raketku-dlya-bolshogo-tennisa-5.jpg	
57	Бадмінтон	2025-09-19 18:00:00	2025-09-20 10:54:35	["Кирило", "Віталій", "Anna", "Yuliia P", "bakumvv@gmail.com", "tmbmax"]	[]	{}	https://sportano.ua/blog/wp-content/uploads/2024/01/Badminton-zasady-gry.jpg	ВІДМІНА!!!\r\nДрузі, у вечір п'ятниці ми не можемо забукати корти - вони просто недоступні від самого початку. Нажаль.\r\n
58	Бадмінтон  	2025-09-23 19:00:00	2025-09-23 19:05:27	["Ilona", "tmbmax", "Кирило", "Наталія Овсієнко ", "Ruslan R.", "helga_r80@icloud.com"]	["Olga Mc"]	{"Грає в інший день": ["Ruslan R.", "helga_r80@icloud.com"]}	\N	
59	Бадмінтон  	2025-09-24 19:00:00	2025-09-24 19:40:20	["Karyna", "tmbmax", "Наталія Овсієнко ", "Ruslan R.", "Anna", "Віталій", "Хтось", "Світлана", "Jeff"]	[]	{"Грає в інший день": ["Ruslan R."]}	\N	
60	Бадмінтон  	2025-09-25 19:00:00	2025-09-25 19:12:23	["Yuliia P", "tmbmax", "Кирило", "Karyna", "Ruslan R.", "helga_r80@icloud.com", "Віталій", "Світлана", "Jeff"]	[]	{"Грає в інший день": ["Karyna", "Кирило", "tmbmax"]}	\N	
61	Бадмінтон  	2025-09-26 10:00:00	2025-09-26 10:19:05	["Кирило", "Ilona", "Yuliia P", "Dmamp"]	[]	{}	\N	
62	Теніс	2025-09-26 18:00:00	2025-09-26 19:14:39	["tmbmax", "Хтось"]	["Ilona", "Кирило", "Dmamp"]	{}	\N	Теніс ми відміняємо на сьогодні!
63	Бадмінтон  	2025-09-28 16:00:00	2025-09-28 16:19:35	["tmbmax", "Yuliia P", "Karyna", "Dmamp", "helga_r80@icloud.com", "Jeff", "Світлана"]	["Ruslan R."]	{}	\N	
64	Бадмінтон	2025-09-29 19:00:00	2025-09-29 20:08:47	["tmbmax", "Karyna", "Наталія Овсієнко ", "Ilona"]	["Ruslan R."]	{}	\N	
65	Бадмінтон	2025-09-30 19:00:00	2025-09-30 19:38:04	["Ruslan R.", "tmbmax", "helga_r80@icloud.com", "Наталія Овсієнко ", "Jeff", "Світлана", "Maria", "George", "Karyna"]	[]	{"Грає в інший день": ["tmbmax"]}	\N	
67	Бадмінтон	2025-10-02 19:00:00	2025-10-02 20:41:34	["Ruslan R.", "tmbmax", "helga_r80@icloud.com", "Хтось", "Yuliia P", "Karyna", "Кирило", "Віталій"]	[]	{}	\N	
68	Бадмінтон	2025-10-03 10:00:00	2025-10-03 10:14:41	["Кирило", "Dmamp", "Ilona", "Yuliia P"]	[]	{}	\N	
69	Теніс	2025-10-03 18:00:00	2025-10-03 18:02:59	["tmbmax", "Хтось", "Кирило", "Ilona"]	[]	{}	\N	
70	Бадмінтон	2025-10-05 16:00:00	2025-10-05 16:04:25	["Ruslan R.", "tmbmax", "helga_r80@icloud.com", "Karyna"]	["Наталія Овсієнко "]	{}	\N	
71	Бадмінтон  	2025-10-06 19:00:00	2025-10-06 19:04:46	["Наталія Овсієнко ", "Karyna", "tmbmax"]	["Olena A"]	{}	\N	
72	Бадмінтон  	2025-10-07 19:00:00	2025-10-07 19:22:14	["Ilona", "Світлана", "Jeff", "helga_r80@icloud.com"]	["Кирило", "Olha D", "tmbmax"]	{}	\N	
73	Бадмінтон  	2025-10-08 19:00:00	2025-10-08 20:03:02	["Наталія Овсієнко ", "Karyna", "Anna", "Світлана", "Jeff", "Хтось", "tmbmax", "Olena A"]	["Maria"]	{"Грає в інший день": ["tmbmax"]}	\N	
74	Бадмінтон  	2025-10-09 19:00:00	2025-10-09 19:09:45	["Кирило", "bakumvv@gmail.com", "Karyna", "Віталій", "helga_r80@icloud.com", "Anna", "tmbmax", "Olha D"]	["Yuliia P"]	{"Грає в інший день": ["Karyna"]}	\N	
75	Бадмінтон  	2025-10-10 10:00:00	2025-10-10 10:21:26	["Кирило", "Yuliia P", "bakumvv@gmail.com", "Dmamp"]	[]	{}	\N	
76	Теніс	2025-10-10 18:00:00	2025-10-10 18:14:01	["tmbmax", "nadiiab"]	["Кирило"]	{}	\N	
77	Бадмінтон  	2025-10-12 16:00:00	2025-10-12 16:06:05	["Karyna", "Olha D", "Наталія Овсієнко ", "Ruslan R."]	["tmbmax"]	{}	\N	
\.


--
-- Data for Name: poll; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.poll (id, question, options_json, voted_users_json, date, author) FROM stdin;
2	До вересня в будні дні для мене було б зручно грати у	[{"text": "18:00", "votes": 3}, {"text": "19:00", "votes": 8}]	["Наталія Овсієнко ", "Olena A", "Ilona", "Кирило", "Karyna", "Ruslan R.", "Olga Mc", "helga_r80@icloud.com", "tmbmax"]	2025-07-20 17:00:06	Кирило
1	В які дні краще грати в волейбол?	[{"text": "Вівторок", "votes": 0}, {"text": "Субота", "votes": 5}]	["Vitalij", "Наталія Овсієнко ", "Кирило", "tmbmax", "Laluhovy"]	2025-07-03 06:25:17	Кирило
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."user" (id, username, password_hash, role, has_paid_fees, last_fee_payment_date, email, email_confirmed, email_confirmation_token, nickname, seen_items_json) FROM stdin;
10	Vitalij	scrypt:32768:8:1$E6KmbaE22uZIHs8L$2776c5270e9f40ca14619af07530dacfa6045bc6404c2f8cd4d4a37d0e27018488e5e239c316f165c7985c90825844df3aa21a397aecc466a86eeae91e0df700	user	t	2025-07-05	ksusairbe@icloud.com	t	\N	\N	{"polls": [1, 2], "announcements": [1]}
5	Olena A	scrypt:32768:8:1$TbeI9QfHAEFV5ttB$50635a4a53932b14afaff363cf29b278bbe7b1246c5a685b8c28e8abbf37aef9e1933a557174e67528ea51ee13eb3503e0ea4277c5ed9eee9626c94583fbbf1d	user	t	2025-07-05	verona.olenka@gmail.com	t	\N	\N	{"announcements": [1, 3], "polls": [1, 2]}
3	Anna	scrypt:32768:8:1$h2d7ZPVccXYor9DI$94550fbacf2b0f4361ee4dcb7f9e54badf82f64cd0b8a237fa9c004016bb5dbcddc1dcc947ba47294e63b22c5adf939bc1548884598822fec68dc8cadb7274ed	user	t	2025-07-02	dubtschak@ukr.net	t	\N	\N	\N
26	tmbmax	scrypt:32768:8:1$9i8RB9xSaMGzIfIF$08c1786db4e89874c53905a348a7362ce8b2e6c3d04630718015d31eb882a02634a6cb5a3cca3b035d2b1917442adb03bcbeac6bec129612aa5caae002228bc7	user	f	\N	tmbmax@yahoo.co.uk	t	\N	Tanya MB	{"announcements": [1, 3, 4, 5, 6], "polls": [1, 2]}
14	helga_r80@icloud.com	scrypt:32768:8:1$g0YL5WsDMCULut51$d83ce91d1487c3dfed6639850217c45bca39ca46e477b33bf35db539862af7785958231a93239a238590b02327363b463c394bd4770dae2db231b68c87638817	user	t	2025-07-05	helga_r80@icloud.com	t	\N	Оля Р	{"announcements": [1, 3, 4, 5, 6, 7, 8], "polls": [1, 2]}
8	Nadiia Johnson	scrypt:32768:8:1$hoL1d9kHnUluwIhy$b92287cd3bcc7d5b73c1fa7f6494a8095ec40568f7740478b1c0c1d795d36d6a0a1f48935a90ef0b37def9d68070c90d014b7864bf6b7e60fbcc1010f06be921	user	f	\N	johnsonnadiia@gmail.com	t	\N	\N	\N
19	Gedeon347	scrypt:32768:8:1$AMMKFNUfFSIEPLfj$cbcfe53d4ecfdbab1eac2b97fa819a40ea8493962ff7db05da5fbd2410d8d8420de81721b847ab09f21cb30bbe42a28b3ea6a2ceeea015985bb584e6d84a75d7	user	t	2025-07-15	gedeon347140390@gmail.com	t	\N	Сергій	\N
18	Oleksandra 	scrypt:32768:8:1$hZ6OydgrBKUQ5aik$e26edcb7927b85fe8018190def263f7ab5543c6c55c8443d4585b9283249c9b26999dfe6cbbeaa57e013729abb4b30d8277296d8a95e06609eda03d00eb497a7	user	t	2025-07-15	Sashashylina@gmail.com	t	\N	\N	\N
15	Lesia	scrypt:32768:8:1$xgzAJalRz9fSGCfg$c1e75f111bd14bab265bfb16863c485ab06104352cc9a4da9742d649a552331b8bb285add0be8fa2b988cb6f8bf6d9cad0b28ed2f111d90b8b996167a6cbe8e1	user	f	\N	lisenya03@gmail.com	t	\N	\N	\N
11	Karyna	scrypt:32768:8:1$VVKQlaIXAajj0qUO$0f7beb81378f4d8394093ee44af09a5e782614f6441d9b08747dcc47dc374cc8a5dbbfd489c2168934cbd670e2e38eea1276a52d709f0fd588e8feb438389120	user	t	2025-07-01	karynabakumenko@gmail.com	t	\N	\N	{"announcements": [1], "polls": [1, 2]}
12	Наталія Овсієнко 	scrypt:32768:8:1$uXUjbN5hCZTheHGP$fae28e27292f885d91d0c918d6cd4e2a6abd006701daabf273621f6132e2e4104dd7db99a92870d37df5f87628954392926ad3992158d26b7e126d2b9db550e3	user	t	2025-07-10	ovsienkonatasha@gmail.com	t	\N	Наталі	{"polls": [1, 2], "announcements": [1, 3, 4]}
16	Ruslan R.	scrypt:32768:8:1$qxhzz0InwVoRv4o5$a9a126639f0838423fcd6cd01c4fe4d0516238dae38def246fa102107de15638116b560eb5fe9a8c81c19f83208f325e99dba0977565608a7270edf6ea9fc6c3	user	t	2025-07-05	razovyrm@gmail.com	t	\N	\N	{"announcements": [1, 3], "polls": [1, 2]}
7	Olga Mc	scrypt:32768:8:1$zso5wXBkVk4MERdq$aaea6990c036ec4923c29d80daae003f1e6dbd8eac0efe174ac2faec360db98d7c3c5ca8423851675066ba71ed177c1b8a194b5bdb39e39535bcc4e768c08fe1	user	t	2025-07-29	olga.mcmahon@gmail.com	t	\N	\N	{"announcements": [1, 3, 4, 5, 6, 7, 8], "polls": [1, 2]}
28	tatiana.shechkova@gmail.com	scrypt:32768:8:1$5xL1kqAU5QRfFP6p$e52cb06e61adf384f3affca0c509390288379b583104af5563bafee59e0f892cf7dfb15bb30bf185e04d38b179de803d0278939cbbf5c2c95b5ee869ed2ca0d6	user	f	\N	tatiana.shechkova@gmail.com	t	\N	Tatianka	{}
21	Jeff	scrypt:32768:8:1$bp1Mwcn066Q2SkSA$374ac54da6c2d5e6b64d4898b0d1e2a781e53e718cf1c553f9589026dcff075d0b573e13022e1b375f948e7c887d2ecd8ea49c9a6ca759bfdaf805f969b7b5d9	user	t	2025-07-05	jeffreydavidsmith@hotmail.com	t	\N	\N	\N
27	Natali	scrypt:32768:8:1$NgxjwUAwQQ7NrPEc$deb7698dd5199e6e4dc9ffcc8b13a12f00a3971a7e32380a0769d7c72a6563496f9815e5e6652a098657c59be3e1bcd68fc3595767b74cda059b89a22ab88fe9	user	f	\N	natali_g80@ukr.net	t	\N	Tusia	{}
29	Віталій	scrypt:32768:8:1$ltZaZ5xFpDpDJC6R$2db7e0f1798cf9d1bf657642d5537d82259670e972f5c30804f2ca0555ca8840a36bba4f5b6a38bb0930dd27d28037f70dc75b957bffa7a8cace20f9c3e4b0c1	user	f	\N	vitalijirbe@icloud.com	t	\N	Vitaly	{"announcements": [1, 3, 4, 5, 6]}
23	Ilona	scrypt:32768:8:1$D7FmJ40D1aVoXzgM$5221961a11b8fa8db79e989f3e408f74c8e917c65800b3d46bae694b1ac7ea0d0540e66513905c63a86a1223bad15ac14e0f510ffca2aad8af4b388081cb8920	user	t	2025-07-01	5159043@gmail.com	t	\N	\N	{"announcements": [1, 3, 4, 5, 6], "polls": [1, 2]}
17	Yuliia P	scrypt:32768:8:1$72i83cATnERWrh8P$9ad67cf043e12e598696691eb0b8edad398ebf22048f5c7e23e90388acb4f1667f95e5b9b3570931007766bb12800e7946fcc7c49ab62af39e0aa0ea1576eeb1	superuser	f	\N	efimiyanos@gmail.com	t	\N	брЮлік	{"polls": [1, 2], "announcements": [1, 3, 4, 5, 6, 7, 8]}
2	Кирило	scrypt:32768:8:1$P6iR51Su8mIPQxXJ$e145ed56f623b834633aec1a0492a2d084714b6ae8bfd5e8c2565afb4980e3e7f8901c8c4061c98df004ff55b55c1a6895e98487f60cead18f73d52c90bab4be	admin	t	2025-07-03	kirill.grig.2000@gmail.com	t	\N	\N	{"polls": [1, 2], "announcements": [1, 3, 4, 5, 6, 7, 8, 9]}
20	Світлана	scrypt:32768:8:1$Zkg2Z8DN8e4ENw3a$fe3037cc0a3bc0e14ee710b6b8bfba89d9dcba19b1d127a10bca5d6b36e501fdd42803f60eff67c7e5cc992786714a5c0eb742c358b7292e3263cd1c12fde083	user	t	2025-07-05	Spkonon8@gmail.com	t	\N	\N	{"announcements": [1, 3, 4, 5, 6, 7, 8], "polls": [1, 2]}
30	bakumvv@gmail.com	scrypt:32768:8:1$oU5TqovqUpZF5rci$b33606b4ef058a205b2c601060e87b786691f9231752f67b6bf4b603e9d420be3a591b1d8725f78eb1eb4a50e1ffbe3467a5c9fde7aab777e16fc988bddb416d	user	f	\N	bakumvv@gmail.com	t	\N	Viktor	{}
13	Хтось	scrypt:32768:8:1$tsRFNNfFyOmcqUKK$7b1bb1fc2a945c2545554c4232f7fabf87635ab21585e9dd6751251ae8e60770646292c32c63624d1683522a6c584d3a0c406d3edf1fd8901cdde46bed90c467	user	t	2025-07-05	nazaretto@gmail.com	t	\N	Назаріус	{"polls": [1, 2], "announcements": [1, 3, 4, 5, 6]}
22	Denys	scrypt:32768:8:1$hevag4RvmWFZBaDJ$3ffcff6a56970fa7913e059f390c3fd0b8d922adb17b1974ec6c6f3b57e5e2d62e0f8e6851a8d4b6b398bcda5c0b02ebc9721fa1cbde3e04909bc8dcf0a61db4	user	f	\N	kobets2402@gmail.com	t	\N	\N	\N
31	Dmamp	scrypt:32768:8:1$2s3ISI9IbRdPI4h4$c509b598306a54c1c8a1dfa72aed2ef3ebcd34c3c82962572338914d309df591a3af0d6776e827b3d8ac692d0733474143a61d004efc3e75ab292237c51b5f2f	user	f	\N	ampilogovd@gmail.com	t	\N	Dima	{"announcements": [1, 3, 4, 5, 6], "polls": [1, 2]}
9	Olha D	scrypt:32768:8:1$sOqIKGmREvXB9rof$654785582ad14eeb754f3e3765eae30d875679767f93588816dac0e4734fb82863181645b481c8ee1fd533d71a3b65bfb4c06deeffa80d982266593874475a91	user	t	2025-07-05	olyader49@gmail.com	t	\N	\N	{"polls": [1, 2], "announcements": [1, 3, 4, 5, 6, 7, 8]}
33	George	scrypt:32768:8:1$91bGk1A4L66DMKbZ$4f16744e86de8e75e4bea28bcbc4f1896dfe014399d03815c8c8a3dea9dad43a2371dbd509509e444d0ae3a40a1a4fdbf606fa95a81eb622aba4c2aa3ee869e7	user	f	\N	vanilakanfetk@gmail.com	t	\N	George	{"announcements": [1, 3, 4, 5, 6]}
34	sokraticus	scrypt:32768:8:1$7T5E75pLiUYUWHyM$8062497b1ac6b31435498ec97253f54100358f9f8256a4a675b81e2e88f07b60f95d11a23b574952c9a52ae3d36d96a7368547e24e84559aedd344db239e2ed6	user	f	\N	kuznietsov.yaroslav@gmail.com	t	\N	Ярослав Кузнєцов	{"announcements": [1, 3, 4, 5, 6], "polls": [1, 2]}
32	Maria	scrypt:32768:8:1$FChsZBrvuRzOLDfO$edf688a882d932695cf4b0171b0e9718cd354846ed710151de5f3c75b90a9e3ff72510ca7eaaa1b5c96885d61a9dac087f665734c560e16ae7072fd21af78304	user	f	\N	tatadzemaria@gmail.com	t	\N	MariaT	{}
36	nadiiab	scrypt:32768:8:1$VVJvOiUqf8Ai36k2$bd9474b756cdb866d8acf42b42c5d015a5aead8d7fb8ad4d9808b4b2814073c1fe242827d2076715e6da859cc0ae457c8e556b08cd08db2c40a9decb9c59b3b0	user	f	\N	nada.shanya@gmail.com	t	\N	Nadiia	{}
35	Laluhovy	scrypt:32768:8:1$XbYTFBfBfNHpQhUQ$3c92b0920709746fd25306440fa3f2d439a283b1bcf4b7151757deaa8a39b1261972015c7da70ffb9ad3c166f4bdd80a23f2c8b25556faed11f901c7cdd7db0e	user	f	\N	oleksiiluhovyi@gmail.com	t	\N	Олексій	{"announcements": [1, 3, 4, 5, 6, 7, 8], "polls": [1, 2]}
\.


--
-- Name: announcement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.announcement_id_seq', 9, true);


--
-- Name: event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_id_seq', 84, true);


--
-- Name: financial_transaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.financial_transaction_id_seq', 79, true);


--
-- Name: game_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.game_log_id_seq', 77, true);


--
-- Name: poll_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.poll_id_seq', 2, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_id_seq', 36, true);


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
-- PostgreSQL database dump complete
--

