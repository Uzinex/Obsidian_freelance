import { useMemo, useState } from 'react';
import { Controller } from 'react-hook-form';

export default function SkillSelector({ control, name, skills }) {
  const [search, setSearch] = useState('');

  const groupedSkills = useMemo(() => {
    const groups = {};
    (skills || []).forEach((skill) => {
      const group = skill.category?.name || skill.category || 'Другие навыки';
      if (!groups[group]) {
        groups[group] = [];
      }
      groups[group].push(skill);
    });
    return groups;
  }, [skills]);

  const filteredGroups = useMemo(() => {
    if (!search.trim()) return groupedSkills;
    const lower = search.toLowerCase();
    return Object.fromEntries(
      Object.entries(groupedSkills)
        .map(([group, list]) => [group, list.filter((skill) => skill.name.toLowerCase().includes(lower))])
        .filter(([, list]) => list.length > 0),
    );
  }, [groupedSkills, search]);

  return (
    <Controller
      control={control}
      name={name}
      render={({ field }) => {
        const value = Array.isArray(field.value) ? field.value.map(Number) : [];

        const toggleSkill = (skillId) => {
          const numericId = Number(skillId);
          const exists = value.includes(numericId);
          const next = exists ? value.filter((item) => item !== numericId) : [...value, numericId];
          field.onChange(next);
        };

        return (
          <div className="skill-selector">
            <div className="skill-selector-header">
              <label htmlFor={`${name}-search`}>Навыки</label>
              <input
                id={`${name}-search`}
                type="search"
                placeholder="Поиск по навыкам"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>
            <div className="skill-groups">
              {Object.keys(filteredGroups).length === 0 ? (
                <div className="empty-state">Ничего не найдено. Попробуйте другой запрос.</div>
              ) : (
                Object.entries(filteredGroups).map(([group, list]) => (
                  <div key={group} className="skill-group">
                    <h4>{group}</h4>
                    <div className="skill-chips">
                      {list.map((skill) => {
                        const selected = value.includes(Number(skill.id));
                        return (
                          <button
                            key={skill.id}
                            type="button"
                            className={selected ? 'chip active' : 'chip'}
                            onClick={() => toggleSkill(skill.id)}
                          >
                            {skill.name}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))
              )}
            </div>
            <small className="skill-helper">Выбрано: {value.length}</small>
          </div>
        );
      }}
    />
  );
}
