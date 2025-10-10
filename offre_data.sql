--
-- PostgreSQL database dump
--

\restrict HYzn47xDfrN02O8hBlbHvlTN8ryS6FFi55cqWTCAAubIKMroXdadQhP3jZaJa88

-- Dumped from database version 14.18
-- Dumped by pg_dump version 14.19 (Homebrew)

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

--
-- Data for Name: tickets_bah_offre; Type: TABLE DATA; Schema: public; Owner: olympique_user
--

INSERT INTO public.tickets_bah_offre (id, nom, description, prix, nombre_de_places, "createdAt", "updatedAt") VALUES (1, 'duo', 'pour un couple et un enfant', 100, '3', '2025-06-17 01:42:48.882153+02', '2025-06-17 01:42:48.894664+02');
INSERT INTO public.tickets_bah_offre (id, nom, description, prix, nombre_de_places, "createdAt", "updatedAt") VALUES (2, 'familly', 'pour une famille', 230, '5', '2025-06-17 01:43:14.339816+02', '2025-06-17 01:43:14.341233+02');
INSERT INTO public.tickets_bah_offre (id, nom, description, prix, nombre_de_places, "createdAt", "updatedAt") VALUES (3, 'TRIO', 'CETTE FORMULE EST IDEAL', 250, '3', '2025-10-08 15:49:12.367428+02', '2025-10-08 15:49:12.37006+02');
INSERT INTO public.tickets_bah_offre (id, nom, description, prix, nombre_de_places, "createdAt", "updatedAt") VALUES (4, 'QUATRIO', 'CETTE FORMULE EST IDEAL', 300, '4', '2025-10-08 15:49:34.850307+02', '2025-10-08 15:49:34.852214+02');
INSERT INTO public.tickets_bah_offre (id, nom, description, prix, nombre_de_places, "createdAt", "updatedAt") VALUES (5, 'PROMOS', 'CETTE FORMULE EST IDEAL', 400, '6', '2025-10-08 15:50:45.984332+02', '2025-10-08 15:50:45.986208+02');
INSERT INTO public.tickets_bah_offre (id, nom, description, prix, nombre_de_places, "createdAt", "updatedAt") VALUES (6, 'FIDELITE', 'CETTE FORMULE EST IDEAL', 596, '7', '2025-10-08 15:51:08.792769+02', '2025-10-08 15:51:08.794545+02');


--
-- Name: tickets_bah_offre_id_seq; Type: SEQUENCE SET; Schema: public; Owner: olympique_user
--

SELECT pg_catalog.setval('public.tickets_bah_offre_id_seq', 6, true);


--
-- PostgreSQL database dump complete
--

\unrestrict HYzn47xDfrN02O8hBlbHvlTN8ryS6FFi55cqWTCAAubIKMroXdadQhP3jZaJa88

