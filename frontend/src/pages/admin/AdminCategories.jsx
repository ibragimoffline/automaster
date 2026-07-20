import { useEffect, useState } from 'react';
import { Plus, Trash2, Check, X, Pencil } from 'lucide-react';
import { api } from '../../api/client';
import { useToast } from '../../components/Toast';

export default function AdminCategories() {
  const toast = useToast();
  const [cats, setCats] = useState(null);
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [editing, setEditing] = useState(null);

  const load = () => api.adminCategories()
    .then((d) => setCats(Array.isArray(d) ? d : d.results || []))
    .catch(() => { setCats([]); toast.error('Kategoriyalar yuklanmadi'); });

  useEffect(() => { load(); }, []);

  const create = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      await api.adminCreateCategory({ name: name.trim(), description: desc.trim() });
      setName(''); setDesc(''); toast.success('Kategoriya qo\'shildi'); load();
    } catch (er) { toast.error(er.message || 'Qo\'shib bo\'lmadi'); }
  };

  const saveEdit = async () => {
    try {
      await api.adminUpdateCategory(editing.id, { name: editing.name, description: editing.description });
      setEditing(null); toast.success('Saqlandi'); load();
    } catch (er) { toast.error(er.message || 'Saqlab bo\'lmadi'); }
  };

  const remove = async (c) => {
    if (!window.confirm(`"${c.name}" kategoriyasini o'chirasizmi?`)) return;
    try {
      await api.adminDeleteCategory(c.id);
      setCats((list) => list.filter((x) => x.id !== c.id));
      toast.success('O\'chirildi');
    } catch (er) { toast.error(er.message || 'O\'chirib bo\'lmadi'); }
  };

  return (
    <div className="apage">
      <form className="acat-add card" onSubmit={create}>
        <input className="input" placeholder="Yangi kategoriya nomi" value={name} onChange={(e) => setName(e.target.value)} aria-label="Nomi" />
        <input className="input" placeholder="Tavsif (ixtiyoriy)" value={desc} onChange={(e) => setDesc(e.target.value)} aria-label="Tavsif" />
        <button className="btn" type="submit"><Plus size={16} /> Qo'shish</button>
      </form>

      {cats === null ? (
        <div className="skeleton" style={{ height: 280, borderRadius: 14 }} />
      ) : (
        <div className="atable-wrap card">
          <table className="atable">
            <thead><tr><th>Nomi</th><th>Tavsif</th><th className="ta-c">Ustalar</th><th className="ta-c">Xizmatlar</th><th></th></tr></thead>
            <tbody>
              {cats.map((c) => (
                <tr key={c.id}>
                  {editing?.id === c.id ? (
                    <>
                      <td><input className="input input--sm" value={editing.name} onChange={(e) => setEditing({ ...editing, name: e.target.value })} /></td>
                      <td><input className="input input--sm" value={editing.description || ''} onChange={(e) => setEditing({ ...editing, description: e.target.value })} /></td>
                      <td className="ta-c mono">{c.master_count}</td>
                      <td className="ta-c mono">{c.service_count}</td>
                      <td className="ta-r acell-actions">
                        <button className="aicon-btn aicon-btn--ok" onClick={saveEdit} title="Saqlash"><Check size={16} /></button>
                        <button className="aicon-btn" onClick={() => setEditing(null)} title="Bekor"><X size={16} /></button>
                      </td>
                    </>
                  ) : (
                    <>
                      <td><strong>{c.name}</strong></td>
                      <td className="acell-sub">{c.description || '—'}</td>
                      <td className="ta-c mono">{c.master_count}</td>
                      <td className="ta-c mono">{c.service_count}</td>
                      <td className="ta-r acell-actions">
                        <button className="aicon-btn" onClick={() => setEditing({ id: c.id, name: c.name, description: c.description })} title="Tahrirlash"><Pencil size={15} /></button>
                        <button className="aicon-btn aicon-btn--danger" onClick={() => remove(c)} title="O'chirish"><Trash2 size={16} /></button>
                      </td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
          {cats.length === 0 && <div className="empty"><strong>Kategoriya yo'q</strong></div>}
        </div>
      )}
    </div>
  );
}
