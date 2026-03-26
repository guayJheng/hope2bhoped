--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2 (Debian 17.2-1.pgdg120+1)
-- Dumped by pg_dump version 17.2

-- Started on 2026-03-20 19:39:44

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- TOC entry 220 (class 1259 OID 16398)
-- Name: logs; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.logs (
    lid integer NOT NULL,
    pzid integer,
    play_time double precision,
    action_count integer,
    list_movement_time text,
    hit_count integer,
    result boolean
);


ALTER TABLE public.logs OWNER TO myuser;

--
-- TOC entry 219 (class 1259 OID 16397)
-- Name: logs_lid_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

ALTER TABLE public.logs ALTER COLUMN lid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.logs_lid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 218 (class 1259 OID 16390)
-- Name: puzzles; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.puzzles (
    pzid integer NOT NULL,
    name text,
    fitts_id double precision,
    base_diff double precision,
    total_hit integer,
    dmg_per_hit double precision
);


ALTER TABLE public.puzzles OWNER TO myuser;

--
-- TOC entry 217 (class 1259 OID 16389)
-- Name: puzzles_pzid_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

ALTER TABLE public.puzzles ALTER COLUMN pzid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.puzzles_pzid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 3368 (class 0 OID 16398)
-- Dependencies: 220
-- Data for Name: logs; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.logs (lid, pzid, play_time, action_count, list_movement_time, hit_count, result) FROM stdin;
\.


--
-- TOC entry 3366 (class 0 OID 16390)
-- Dependencies: 218
-- Data for Name: puzzles; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.puzzles (pzid, name, fitts_id, base_diff, total_hit, dmg_per_hit) FROM stdin;
\.


--
-- TOC entry 3374 (class 0 OID 0)
-- Dependencies: 219
-- Name: logs_lid_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.logs_lid_seq', 1, false);


--
-- TOC entry 3375 (class 0 OID 0)
-- Dependencies: 217
-- Name: puzzles_pzid_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.puzzles_pzid_seq', 1, false);


--
-- TOC entry 3218 (class 2606 OID 16404)
-- Name: logs logs_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.logs
    ADD CONSTRAINT logs_pkey PRIMARY KEY (lid);


--
-- TOC entry 3216 (class 2606 OID 16396)
-- Name: puzzles puzzles_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.puzzles
    ADD CONSTRAINT puzzles_pkey PRIMARY KEY (pzid);


--
-- TOC entry 3219 (class 2606 OID 16405)
-- Name: logs puzzles_logs_pzid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.logs
    ADD CONSTRAINT puzzles_logs_pzid_fkey FOREIGN KEY (pzid) REFERENCES public.puzzles(pzid) NOT VALID;


-- Completed on 2026-03-20 19:39:45

--
-- PostgreSQL database dump complete
--

