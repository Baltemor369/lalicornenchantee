"use strict";

const VERSION = "3.0.0";
const DATE = "19/10/2026";

// Foyers de référence (coordonnées OpenStreetMap, identiques à la version Streamlit)
const FOYERS = {
    flavigny: { nom: "Flavigny", lat: 49.0868385, lon: 5.9621080 },
    hablainville: { nom: "Hablainville", lat: 48.5180357, lon: 6.7284065 },
};

const BASE_PRICE = 70;
const OUT_PRICE = 100;
const LUXEMBOURG_PRICE = 90;

// Paliers : distance max à Flavigny, et distance max à Hablainville (null = pas de condition)
const PALIERS = [
    { maxFlavigny: 25, maxHablainville: null, prix: BASE_PRICE },
    { maxFlavigny: 50, maxHablainville: null, prix: BASE_PRICE + 5 * 1 },
    { maxFlavigny: 75, maxHablainville: null, prix: BASE_PRICE + 5 * 2 },
    { maxFlavigny: 108, maxHablainville: 100, prix: BASE_PRICE + 5 * 3 },
    { maxFlavigny: 145, maxHablainville: 100, prix: BASE_PRICE + 5 * 4 },
    { maxFlavigny: 170, maxHablainville: 100, prix: BASE_PRICE + 5 * 5 },
];

// Distance géodésique sur l'ellipsoïde WGS84 (formule de Vincenty), en km.
// Même résultat que geopy.distance.geodesic au mètre près.
function distanceKm(lat1, lon1, lat2, lon2) {
    const a = 6378137.0;
    const f = 1 / 298.257223563;
    const b = a * (1 - f);
    const rad = Math.PI / 180;
    const L = (lon2 - lon1) * rad;
    const U1 = Math.atan((1 - f) * Math.tan(lat1 * rad));
    const U2 = Math.atan((1 - f) * Math.tan(lat2 * rad));
    const sinU1 = Math.sin(U1), cosU1 = Math.cos(U1);
    const sinU2 = Math.sin(U2), cosU2 = Math.cos(U2);

    let lambda = L, prev, sinSigma, cosSigma, sigma, cosSqAlpha, cos2SigmaM;
    let iter = 0;
    do {
        const sinLambda = Math.sin(lambda), cosLambda = Math.cos(lambda);
        sinSigma = Math.sqrt((cosU2 * sinLambda) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda) ** 2);
        if (sinSigma === 0) return 0;
        cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLambda;
        sigma = Math.atan2(sinSigma, cosSigma);
        const sinAlpha = (cosU1 * cosU2 * sinLambda) / sinSigma;
        cosSqAlpha = 1 - sinAlpha ** 2;
        cos2SigmaM = cosSqAlpha !== 0 ? cosSigma - (2 * sinU1 * sinU2) / cosSqAlpha : 0;
        const C = (f / 16) * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha));
        prev = lambda;
        lambda = L + (1 - C) * f * sinAlpha *
            (sigma + C * sinSigma * (cos2SigmaM + C * cosSigma * (-1 + 2 * cos2SigmaM ** 2)));
    } while (Math.abs(lambda - prev) > 1e-12 && ++iter < 200);

    const uSq = (cosSqAlpha * (a * a - b * b)) / (b * b);
    const A = 1 + (uSq / 16384) * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)));
    const B = (uSq / 1024) * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)));
    const deltaSigma = B * sinSigma * (cos2SigmaM + (B / 4) * (cosSigma * (-1 + 2 * cos2SigmaM ** 2) -
        (B / 6) * cos2SigmaM * (-3 + 4 * sinSigma ** 2) * (-3 + 4 * cos2SigmaM ** 2)));
    return (b * A * (sigma - deltaSigma)) / 1000;
}

function calculerTarif(lat, lon, estLuxembourgVille = false) {
    const dFlavigny = distanceKm(lat, lon, FOYERS.flavigny.lat, FOYERS.flavigny.lon);
    const dHablainville = distanceKm(lat, lon, FOYERS.hablainville.lat, FOYERS.hablainville.lon);
    let prix = OUT_PRICE;
    if (estLuxembourgVille) {
        prix = LUXEMBOURG_PRICE;
    } else {
        const palier = PALIERS.find(p =>
            dFlavigny <= p.maxFlavigny && (p.maxHablainville === null || dHablainville <= p.maxHablainville));
        if (palier) prix = palier.prix;
    }
    return { prix, dFlavigny, dHablainville };
}

if (typeof module !== "undefined") {
    module.exports = { distanceKm, calculerTarif, FOYERS, PALIERS };
}

// ---------------------------------------------------------------------------
// Interface
// ---------------------------------------------------------------------------

if (typeof document !== "undefined") {
    const BAN_URL = "https://api-adresse.data.gouv.fr/search/";
    const NOMINATIM_URL = "https://nominatim.openstreetmap.org/search";

    const input = document.getElementById("ville");
    const liste = document.getElementById("suggestions");
    const resultat = document.getElementById("resultat");

    let suggestions = [];
    let actif = -1;
    let debounce = null;
    let requeteBan = null;

    document.getElementById("version").textContent = `v${VERSION} · mise à jour le ${DATE}`;
    remplirGrille();

    input.addEventListener("input", () => {
        clearTimeout(debounce);
        resultat.hidden = true;
        suggestions = [];
        const q = input.value.trim();
        if (q.length < 2) return fermerListe();
        debounce = setTimeout(() => chercherCommunes(q), 200);
    });

    input.addEventListener("keydown", e => {
        if (e.key === "ArrowDown" || e.key === "ArrowUp") {
            if (!suggestions.length) return;
            e.preventDefault();
            const n = suggestions.length;
            actif = e.key === "ArrowDown" ? (actif + 1) % n : (actif <= 0 ? n - 1 : actif - 1);
            afficherListe();
        } else if (e.key === "Enter") {
            e.preventDefault();
            validerSaisie();
        } else if (e.key === "Escape") {
            fermerListe();
        }
    });

    input.addEventListener("blur", () => setTimeout(fermerListe, 150));
    input.addEventListener("focus", () => { if (suggestions.length) afficherListe(); });

    // Entrée avant l'arrivée des suggestions : on attend la recherche puis on prend la première
    async function validerSaisie() {
        if (!suggestions.length) {
            const q = input.value.trim();
            if (q.length < 2) return;
            clearTimeout(debounce);
            await chercherCommunes(q);
        }
        if (suggestions.length) choisir(suggestions[Math.max(actif, 0)]);
    }

    const normaliser = t => t.normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[-']/g, " ").toLowerCase().trim();

    async function chercherCommunes(q) {
        requeteBan?.abort();
        requeteBan = new AbortController();
        const params = new URLSearchParams({
            q, type: "municipality", autocomplete: "1", limit: "6",
            lat: "48.8", lon: "6.3", // favorise le Grand Est
        });
        let communes = [];
        try {
            const rep = await fetch(`${BAN_URL}?${params}`, { signal: requeteBan.signal });
            if (rep.ok) {
                const data = await rep.json();
                communes = data.features.map(f => ({
                    type: "fr",
                    nom: f.properties.city,
                    cp: f.properties.postcode,
                    detail: f.properties.context.split(",").slice(1).join(",").trim(),
                    lat: f.geometry.coordinates[1],
                    lon: f.geometry.coordinates[0],
                }));
            }
        } catch (err) {
            if (err.name === "AbortError") return;
        }
        // Si aucune commune française ne commence par la saisie (ex. « Luxembourg » → Bouy-Luxembourg),
        // c'est sûrement une localité luxembourgeoise : on la propose en premier
        const lu = { type: "lu", nom: q };
        const correspond = communes.some(c => normaliser(c.nom).startsWith(normaliser(q)));
        suggestions = correspond ? [...communes, lu] : [lu, ...communes];
        actif = -1;
        afficherListe();
    }

    function afficherListe() {
        liste.innerHTML = "";
        suggestions.forEach((s, i) => {
            const li = document.createElement("li");
            li.id = `sugg-${i}`;
            li.setAttribute("role", "option");
            li.setAttribute("aria-selected", i === actif ? "true" : "false");
            if (s.type === "fr") {
                li.innerHTML = `<span class="nom"></span> <span class="cp"></span><span class="detail"></span>`;
                li.querySelector(".nom").textContent = s.nom;
                li.querySelector(".cp").textContent = s.cp;
                li.querySelector(".detail").textContent = s.detail;
            } else {
                li.className = "lu";
                li.textContent = `Rechercher « ${s.nom} » au Luxembourg`;
            }
            li.addEventListener("mousedown", e => { e.preventDefault(); choisir(s); });
            liste.appendChild(li);
        });
        liste.hidden = false;
        input.setAttribute("aria-expanded", "true");
        input.setAttribute("aria-activedescendant", actif >= 0 ? `sugg-${actif}` : "");
    }

    function fermerListe() {
        liste.hidden = true;
        input.setAttribute("aria-expanded", "false");
        input.removeAttribute("aria-activedescendant");
    }

    async function nominatim(params) {
        const rep = await fetch(`${NOMINATIM_URL}?${new URLSearchParams({ ...params, format: "json", limit: "1" })}`);
        if (!rep.ok) throw new Error(`Nominatim ${rep.status}`);
        return (await rep.json())[0] || null;
    }

    async function choisir(s) {
        fermerListe();
        suggestions = [];
        afficherChargement();
        try {
            if (s.type === "fr") {
                input.value = `${s.nom} (${s.cp})`;
                // Coordonnées OpenStreetMap pour garder les mêmes tarifs qu'avant, BAN en secours
                let lat = s.lat, lon = s.lon;
                try {
                    const osm = await nominatim({ city: s.nom, postalcode: s.cp, country: "France" });
                    if (osm) { lat = +osm.lat; lon = +osm.lon; }
                } catch { /* coordonnées BAN */ }
                afficherResultat(`${s.nom} (${s.cp})`, calculerTarif(lat, lon));
            } else {
                const osm = await nominatim({ q: s.nom, countrycodes: "lu", featureType: "settlement" });
                if (!osm) return afficherErreur(`Aucune localité « ${s.nom} » trouvée au Luxembourg.`);
                const estVille = osm.addresstype === "city" && /^(luxembourg|lëtzebuerg|luxemburg)$/i.test(osm.name);
                input.value = `${osm.name} (Luxembourg)`;
                afficherResultat(`${osm.name} (Luxembourg)`, calculerTarif(+osm.lat, +osm.lon, estVille));
            }
        } catch {
            afficherErreur("Service de localisation indisponible, réessayez dans un instant.");
        }
    }

    function afficherChargement() {
        resultat.hidden = false;
        resultat.className = "resultat chargement";
        resultat.textContent = "Calcul en cours…";
    }

    function afficherErreur(message) {
        resultat.hidden = false;
        resultat.className = "resultat erreur";
        resultat.textContent = message;
    }

    function afficherResultat(lieu, { prix, dFlavigny, dHablainville }) {
        const km = d => d.toLocaleString("fr-FR", { maximumFractionDigits: 1 });
        resultat.hidden = false;
        resultat.className = "resultat";
        resultat.innerHTML = `
            <p class="lieu"></p>
            <p class="prix">${prix}&nbsp;€</p>
            <p class="distances">${km(dFlavigny)} km de ${FOYERS.flavigny.nom} · ${km(dHablainville)} km d'${FOYERS.hablainville.nom}</p>`;
        resultat.querySelector(".lieu").textContent = lieu;
    }

    function remplirGrille() {
        const tbody = document.querySelector("#grille tbody");
        let min = 0;
        for (const p of PALIERS) {
            const tr = document.createElement("tr");
            const cond = p.maxHablainville ? ` et ≤ ${p.maxHablainville} km d'Hablainville` : "";
            tr.innerHTML = `<td>${min}–${p.maxFlavigny} km de Flavigny${cond}</td><td>${p.prix} €</td>`;
            tbody.appendChild(tr);
            min = p.maxFlavigny;
        }
        tbody.insertAdjacentHTML("beforeend",
            `<tr><td>Luxembourg (ville)</td><td>${LUXEMBOURG_PRICE} €</td></tr>
             <tr><td>Au-delà</td><td>${OUT_PRICE} €</td></tr>`);
    }
}
