import React from 'react';

type TeamMember = {
  name: string;
  email: string;
  github: string;
};

const TeamPage: React.FC = () => {
  const team: TeamMember[] = [
    {
      name: "Sam Elie Seban",
      email: "samseban@icloud.com",
      github: "https://github.com/samseban",
    },
    {
      name: "Daniel Luzzatto",
      email: "luzzattod@gmail.com",
      github: "https://github.com/danielluzzatto",
    },
  ];

    return (
    <section className="mb-12 p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-3xl font-bold text-indigo-700 mb-6">Team</h2>
      <div className="space-y-3">
        {team.map((member) => (
          <div key={member.name} className="text-gray-700">
            <span className="font-semibold">{member.name}</span>
            {' | '}
            <a href={`mailto:${member.email}`} className="text-indigo-600 hover:text-indigo-800">
              {member.email}
            </a>
            {' | '}
            <a href={member.github} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800">
              GitHub
            </a>
          </div>
        ))}
      </div>
    </section>
  );
};

export default TeamPage;