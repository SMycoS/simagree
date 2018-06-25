--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.4
-- Dumped by pg_dump version 10.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: apparition; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.apparition (
    id integer NOT NULL,
    taxon numeric NOT NULL,
    date smallint NOT NULL
);


ALTER TABLE public.apparition OWNER TO postgres;

--
-- Name: identifiants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.identifiants (
    id integer NOT NULL,
    taxon numeric DEFAULT 0 NOT NULL,
    fiche numeric,
    comestible boolean,
    sms boolean,
    a_imprimer boolean,
    lieu text NOT NULL
);


ALTER TABLE public.identifiants OWNER TO postgres;

--
-- Name: identifiants_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.identifiants_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.identifiants_id_seq OWNER TO postgres;

--
-- Name: identifiants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.identifiants_id_seq OWNED BY public.identifiants.id;


--
-- Name: nomenclature; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nomenclature (
    taxon numeric NOT NULL,
    codesyno smallint NOT NULL,
    genre text NOT NULL,
    espece text NOT NULL,
    variete text NOT NULL,
    forme text NOT NULL,
    autorite text NOT NULL,
    moser text NOT NULL,
    biblio1 text,
    biblio2 text,
    biblio3 text
);


ALTER TABLE public.nomenclature OWNER TO postgres;

--
-- Name: noms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.noms (
    id integer NOT NULL,
    taxon numeric DEFAULT 0 NOT NULL,
    nom text DEFAULT ''::text NOT NULL
);


ALTER TABLE public.noms OWNER TO postgres;

--
-- Name: noms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.noms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.noms_id_seq OWNER TO postgres;

--
-- Name: noms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.noms_id_seq OWNED BY public.noms.id;


--
-- Name: notes_eco; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notes_eco (
    id integer NOT NULL,
    taxon numeric NOT NULL,
    notes text NOT NULL,
    ecologie text NOT NULL
);


ALTER TABLE public.notes_eco OWNER TO postgres;

--
-- Name: themes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.themes (
    id integer NOT NULL,
    taxon numeric NOT NULL,
    theme text NOT NULL
);


ALTER TABLE public.themes OWNER TO postgres;

--
-- Name: identifiants id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.identifiants ALTER COLUMN id SET DEFAULT nextval('public.identifiants_id_seq'::regclass);


--
-- Name: noms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.noms ALTER COLUMN id SET DEFAULT nextval('public.noms_id_seq'::regclass);


--
-- Data for Name: apparition; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: identifiants; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: nomenclature; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: noms; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: notes_eco; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: themes; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Name: identifiants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.identifiants_id_seq', 1, false);


--
-- Name: noms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.noms_id_seq', 1, false);


--
-- Name: identifiants identifiants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.identifiants
    ADD CONSTRAINT identifiants_pkey PRIMARY KEY (id);


--
-- Name: identifiants identifiants_taxon_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.identifiants
    ADD CONSTRAINT identifiants_taxon_key UNIQUE (taxon);


--
-- Name: noms noms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.noms
    ADD CONSTRAINT noms_pkey PRIMARY KEY (id);


--
-- Name: apparition unique_apparition_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.apparition
    ADD CONSTRAINT unique_apparition_id UNIQUE (id);


--
-- Name: nomenclature unique_nomenclature_espece; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nomenclature
    ADD CONSTRAINT unique_nomenclature_espece UNIQUE (espece);


--
-- Name: nomenclature unique_nomenclature_genre; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nomenclature
    ADD CONSTRAINT unique_nomenclature_genre UNIQUE (genre);


--
-- Name: notes_eco unique_notes_eco_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes_eco
    ADD CONSTRAINT unique_notes_eco_id UNIQUE (id);


--
-- Name: notes_eco unique_notes_eco_taxon; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes_eco
    ADD CONSTRAINT unique_notes_eco_taxon UNIQUE (taxon);


--
-- Name: themes unique_themes_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.themes
    ADD CONSTRAINT unique_themes_id UNIQUE (id);


--
-- Name: apparition lnk_identifiants_apparition; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.apparition
    ADD CONSTRAINT lnk_identifiants_apparition FOREIGN KEY (taxon) REFERENCES public.identifiants(taxon) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: nomenclature lnk_identifiants_nomenclature; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nomenclature
    ADD CONSTRAINT lnk_identifiants_nomenclature FOREIGN KEY (taxon) REFERENCES public.identifiants(taxon) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: noms lnk_identifiants_noms; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.noms
    ADD CONSTRAINT lnk_identifiants_noms FOREIGN KEY (taxon) REFERENCES public.identifiants(taxon) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: notes_eco lnk_identifiants_notes_eco; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notes_eco
    ADD CONSTRAINT lnk_identifiants_notes_eco FOREIGN KEY (taxon) REFERENCES public.identifiants(taxon) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: themes lnk_identifiants_themes; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.themes
    ADD CONSTRAINT lnk_identifiants_themes FOREIGN KEY (taxon) REFERENCES public.identifiants(taxon) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

