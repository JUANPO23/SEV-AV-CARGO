import React, {useState} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

function App(){
  const [icao,setIcao]=useState('SKUC'); const [data,setData]=useState<any>(null); const [message,setMessage]=useState('');
  async function search(){ setMessage('Consultando...'); try { const airport=await (await fetch(`${API}/airports/${icao}`)).json(); const runways=await (await fetch(`${API}/airports/${icao}/runways`)).json(); const taxiways=await (await fetch(`${API}/airports/${icao}/taxiways`)).json(); const notams=await (await fetch(`${API}/airports/${icao}/notams/live`)).json(); const weather=await (await fetch(`${API}/airports/${icao}/weather/current`)).json(); setData({airport,runways:runways.items,taxiways:taxiways.items,notams,weather}); setMessage(''); } catch(e){setMessage('No fue posible consultar el aeropuerto.');}}
  return <main><header><h1>SEV</h1><p>Pre-evaluación de infraestructura, METAR y NOTAM</p></header><section className="search"><input value={icao} maxLength={4} onChange={e=>setIcao(e.target.value.toUpperCase())}/><button onClick={search}>Investigar OACI</button></section>{message&&<p className="message">{message}</p>}{data&&<section className="grid"><article><h2>{data.airport.name}</h2><p>{data.airport.icao} · {data.airport.location}</p><h3>Pistas</h3><ul>{data.runways.map((r:any)=><li key={r.designator}>RWY {r.designator}: {r.length_m} × {r.width_m} m · {r.pavement?.raw_value||'sin PCN'}</li>)}</ul></article><article><h2>Calles de rodaje</h2><ul>{data.taxiways.map((t:any)=><li key={t.designator}>TWY {t.designator}: {t.width_m} m · {t.pavement?.raw_value||'sin PCN'}</li>)}</ul><h2>Fuentes live</h2><p>NOTAM: {data.notams.status}</p><p>METAR: {data.weather.status}</p></article></section>}<footer>SEV v1 · No calcula performance PEP · Requiere validación operacional</footer></main>}
createRoot(document.getElementById('root')!).render(<App/>);
