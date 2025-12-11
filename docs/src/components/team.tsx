import React from 'react';

type TeamMember = {
  name: string;
  role: string;
  email?: string;
  github?: string;
  website?: string;
};

const TeamPage: React.FC = () => {
  const team: TeamMember[] = [
    {
      name: "Sam Elie Seban",
      role: "Student",
      email: "samseban@icloud.com",
      github: "https://github.com/samseban",
    },
    {
      name: "Daniel Luzzatto",
      role: "Student",
      email: "luzzattod@gmail.com",
      github: "https://github.com/danielluzzatto",
    },
  ];

  const advisors: TeamMember[] = [
    {
      name: "Mani Srivastava",
      role: "Professor",
    },
    {
      name: "Brian Wang",
      role: "PhD Candidate (Mentor)",
    },
  ];

  return (
    <section className="mb-12 p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-3xl font-bold text-indigo-700 mb-6">Team</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h3 className="text-xl font-semibold text-indigo-600 mb-3">Students</h3>
          <div className="space-y-3">
            {team.map((member) => (
              <div key={member.name} className="text-gray-700">
                <span className="font-semibold">{member.name}</span>
                {member.email && (
                  <>
                    {' | '}
                    <a href={`mailto:${member.email}`} className="text-indigo-600 hover:text-indigo-800">
                      {member.email}
                    </a>
                  </>
                )}
                {member.github && (
                  <>
                    {' | '}
                    <a href={member.github} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800">
                      GitHub
                    </a>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-indigo-600 mb-3">Advisors</h3>
          <div className="space-y-3">
            {advisors.map((member) => (
              <div key={member.name} className="text-gray-700">
                <span className="font-semibold">{member.name}</span>
                <span className="text-gray-500"> ({member.role})</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default TeamPage;