'use client'

import { useState } from 'react'
import Header from '@/components/Header'

export default function TermsPage() {
  const [activeSection, setActiveSection] = useState('purpose')

  const sections = [
    { id: 'purpose', title: 'Educational Purpose' },
    { id: 'age', title: 'Age Restrictions' },
    { id: 'research', title: 'Research Consent' },
    { id: 'disclaimers', title: 'Disclaimers' },
    { id: 'privacy', title: 'Privacy & Data' },
    { id: 'liability', title: 'Liability' },
    { id: 'contact', title: 'Contact' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <Header />
      
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-4">
              Terms of Service
            </h1>
            <p className="text-xl text-gray-300 mb-6">
              Educational and Research Platform
            </p>
            <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-4 mb-6">
              <p className="text-yellow-200 font-semibold">
                ⚠️ This platform is for educational and research purposes only. 
                It is NOT a gambling, lottery, or gaming platform.
              </p>
            </div>
          </div>

          {/* Navigation */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 mb-8">
            <div className="flex flex-wrap gap-2">
              {sections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`px-4 py-2 rounded-md font-medium transition-all duration-200 text-sm ${
                    activeSection === section.id
                      ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg"
                      : "text-gray-400 hover:text-white hover:bg-gray-700/50"
                  }`}
                >
                  {section.title}
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="bg-gray-800/30 backdrop-blur-sm rounded-lg p-8">
            {activeSection === 'purpose' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Educational and Research Purpose</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Platform Nature</h3>
                    <p>
                      Billions Bounty is an <strong className="text-yellow-400">educational and research platform</strong> designed to study AI security, human psychology, and manipulation resistance. This platform is NOT a gambling, lottery, or gaming platform.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Research Objectives</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Study AI manipulation resistance techniques</li>
                      <li>Research human psychological patterns in security contexts</li>
                      <li>Advance cybersecurity education and awareness</li>
                      <li>Develop better AI security protocols through controlled testing</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Educational Value</h3>
                    <p>All interactions with the platform are designed to:</p>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Teach users about AI security principles</li>
                      <li>Demonstrate manipulation techniques and their detection</li>
                      <li>Provide insights into cybersecurity best practices</li>
                      <li>Advance academic research in AI safety</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'age' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Age Restrictions and Eligibility</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4">
                    <h3 className="text-xl font-semibold text-red-400 mb-2">Minimum Age Requirement</h3>
                    <ul className="list-disc list-inside space-y-2">
                      <li><strong className="text-white">You must be at least 18 years old</strong> to use this platform</li>
                      <li>Users under 18 are strictly prohibited from accessing the platform</li>
                      <li>We reserve the right to verify age through appropriate means</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Educational Institution Use</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Educational institutions may use this platform for research purposes</li>
                      <li>Institutional users must comply with all applicable laws and regulations</li>
                      <li>Proper supervision required for any educational use</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'research' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Research Consent and Data Usage</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Research Participation</h3>
                    <p>By using this platform, you consent to participate in research activities including:</p>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Analysis of interaction patterns and behaviors</li>
                      <li>Study of manipulation attempt strategies</li>
                      <li>Research on AI security effectiveness</li>
                      <li>Academic publication of anonymized findings</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Data Collection for Research</h3>
                    <p>We collect the following data for research purposes:</p>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Interaction logs and conversation patterns</li>
                      <li>User behavior analytics (anonymized)</li>
                      <li>Security event data</li>
                      <li>Platform usage statistics</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Data Anonymization</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>All personal identifiers are removed from research data</li>
                      <li>Data is aggregated and anonymized before analysis</li>
                      <li>Individual user privacy is protected in all research outputs</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'disclaimers' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Disclaimers and Limitations</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4">
                    <h3 className="text-xl font-semibold text-red-400 mb-2">No Gambling or Lottery Nature</h3>
                    <ul className="list-disc list-inside space-y-2">
                      <li>This platform is <strong className="text-white">NOT</strong> a gambling or lottery system</li>
                      <li>No real money prizes are awarded through the platform</li>
                      <li>All monetary transactions are for research participation fees only</li>
                      <li>The platform does not constitute gambling under any jurisdiction</li>
                    </ul>
                  </div>

                  <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-4">
                    <h3 className="text-xl font-semibold text-yellow-400 mb-2">No Financial Investment</h3>
                    <ul className="list-disc list-inside space-y-2">
                      <li>Do not invest money you cannot afford to lose</li>
                      <li>All fees are for research participation, not investment</li>
                      <li>No financial returns or profits are guaranteed or implied</li>
                      <li>The platform is not a financial investment vehicle</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Educational Tool Only</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>This platform is designed solely for educational and research purposes</li>
                      <li>It should not be used for actual security testing of production systems</li>
                      <li>Results from this platform may not apply to real-world scenarios</li>
                      <li>Users should not rely on this platform for actual security decisions</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'privacy' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Privacy and Data Protection</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Data Security</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>We implement appropriate security measures to protect user data</li>
                      <li>Data is stored securely and access is restricted</li>
                      <li>Regular security audits are conducted</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Data Retention</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Research data may be retained indefinitely for academic purposes</li>
                      <li>Personal data is retained only as long as necessary</li>
                      <li>Users may request data deletion subject to research requirements</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Third-Party Sharing</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Research data may be shared with academic institutions</li>
                      <li>All sharing is done in anonymized form</li>
                      <li>No personal information is shared without consent</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'liability' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Limitation of Liability</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">No Warranties</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>The platform is provided "as is" without warranties</li>
                      <li>We do not guarantee platform availability or performance</li>
                      <li>Users assume all risks associated with platform use</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Limitation of Damages</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Our liability is limited to the maximum extent permitted by law</li>
                      <li>We are not liable for indirect, incidental, or consequential damages</li>
                      <li>Total liability is limited to the amount paid for platform access</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'contact' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Contact Information</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Research Coordinator</h3>
                    <p>For questions about these terms or the research platform:</p>
                    <ul className="list-none space-y-1 ml-4">
                      <li>Email: research@billionsbounty.edu</li>
                      <li>Address: [Research Institution Address]</li>
                      <li>Phone: [Research Institution Phone]</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Privacy Officer</h3>
                    <ul className="list-none space-y-1 ml-4">
                      <li>Email: privacy@billionsbounty.edu</li>
                      <li>Address: [Privacy Office Address]</li>
                    </ul>
                  </div>

                  <div className="bg-blue-500/20 border border-blue-500/50 rounded-lg p-4">
                    <h3 className="text-xl font-semibold text-blue-400 mb-2">Research Ethics Approval</h3>
                    <p>This platform operates under the approval of:</p>
                    <ul className="list-disc list-inside space-y-1 ml-4">
                      <li>[Institution Name] Institutional Review Board (IRB)</li>
                      <li>Protocol Number: [IRB Protocol Number]</li>
                      <li>Approval Date: [Approval Date]</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="text-center mt-8">
            <p className="text-gray-400 text-sm">
              By using this platform, you acknowledge that you have read and understood these terms.
            </p>
            <p className="text-yellow-400 font-semibold mt-2">
              This platform is for educational and research purposes only. It is not a gambling, lottery, or gaming platform.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
