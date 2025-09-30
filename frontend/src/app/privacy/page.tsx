'use client'

import { useState } from 'react'
import Header from '@/components/Header'

export default function PrivacyPage() {
  const [activeSection, setActiveSection] = useState('introduction')

  const sections = [
    { id: 'introduction', title: 'Introduction' },
    { id: 'collection', title: 'Data Collection' },
    { id: 'usage', title: 'Data Usage' },
    { id: 'protection', title: 'Data Protection' },
    { id: 'sharing', title: 'Data Sharing' },
    { id: 'retention', title: 'Data Retention' },
    { id: 'rights', title: 'User Rights' },
    { id: 'security', title: 'Security' },
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
              Privacy Policy
            </h1>
            <p className="text-xl text-gray-300 mb-6">
              Research Platform Data Protection
            </p>
            <div className="bg-blue-500/20 border border-blue-500/50 rounded-lg p-4 mb-6">
              <p className="text-blue-200 font-semibold">
                🔒 Your privacy and data protection are important to us. 
                This platform is designed for educational and research purposes.
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
                      ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg"
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
            {activeSection === 'introduction' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Introduction</h2>
                
                <div className="space-y-4 text-gray-300">
                  <p>
                    This Privacy Policy describes how Billions Bounty ("we," "our," or "us") collects, uses, and protects information when you use our educational and research platform. This platform is designed for academic research into AI security and human psychology.
                  </p>

                  <div className="bg-green-500/20 border border-green-500/50 rounded-lg p-4">
                    <h3 className="text-xl font-semibold text-green-400 mb-2">Research Purpose</h3>
                    <p>
                      Our platform is designed for academic research into AI security, human psychology, and manipulation resistance. All data collection and usage is conducted under strict research ethics guidelines.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'collection' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Information We Collect</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Research Data</h3>
                    <p>We collect the following information for research purposes:</p>
                    
                    <div className="ml-4 space-y-3">
                      <div>
                        <h4 className="font-semibold text-blue-400">Interaction Data:</h4>
                        <ul className="list-disc list-inside space-y-1 ml-4">
                          <li>Conversation logs and chat interactions</li>
                          <li>User behavior patterns and response times</li>
                          <li>Security event data and manipulation attempts</li>
                          <li>Platform usage statistics and session data</li>
                        </ul>
                      </div>

                      <div>
                        <h4 className="font-semibold text-blue-400">Technical Data:</h4>
                        <ul className="list-disc list-inside space-y-1 ml-4">
                          <li>IP addresses (anonymized for research)</li>
                          <li>Browser and device information</li>
                          <li>Platform performance metrics</li>
                          <li>Error logs and debugging information</li>
                        </ul>
                      </div>

                      <div>
                        <h4 className="font-semibold text-blue-400">Demographic Data (Optional):</h4>
                        <ul className="list-disc list-inside space-y-1 ml-4">
                          <li>Age range (18+ only)</li>
                          <li>Educational background (if provided)</li>
                          <li>Research experience level (if provided)</li>
                          <li>Geographic region (general, not specific location)</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Financial Data</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Payment information for research participation fees</li>
                      <li>Transaction records (anonymized)</li>
                      <li>Wallet addresses (for blockchain transactions only)</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'usage' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">How We Use Information</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Research Purposes</h3>
                    <p>We use collected information for:</p>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Academic research on AI security and manipulation resistance</li>
                      <li>Analysis of human psychological patterns in security contexts</li>
                      <li>Development of improved AI security protocols</li>
                      <li>Publication of research findings in academic journals</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Educational Purposes</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Improving the educational value of the platform</li>
                      <li>Developing better learning materials</li>
                      <li>Creating awareness about cybersecurity threats</li>
                      <li>Advancing AI safety education</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Platform Improvement</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Enhancing platform functionality and user experience</li>
                      <li>Identifying and fixing technical issues</li>
                      <li>Optimizing performance and security</li>
                      <li>Developing new research features</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'protection' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Data Anonymization and Protection</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Anonymization Process</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>All personal identifiers are removed from research data</li>
                      <li>Data is aggregated to prevent individual identification</li>
                      <li>Unique identifiers are replaced with research codes</li>
                      <li>Sensitive information is encrypted or removed</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Data Security Measures</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Encryption of data in transit and at rest</li>
                      <li>Access controls and authentication requirements</li>
                      <li>Regular security audits and assessments</li>
                      <li>Secure data storage and backup procedures</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Research Data Handling</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Data is processed only by authorized research personnel</li>
                      <li>Access is logged and monitored</li>
                      <li>Data is stored in secure, access-controlled environments</li>
                      <li>Regular data retention reviews are conducted</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'sharing' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Information Sharing</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Academic Sharing</h3>
                    <p>We may share anonymized research data with:</p>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Academic institutions and researchers</li>
                      <li>Peer-reviewed academic journals</li>
                      <li>Research conferences and presentations</li>
                      <li>Collaborative research partners</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Research Publications</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Research findings may be published in academic journals</li>
                      <li>All publications use only anonymized data</li>
                      <li>No individual user information is disclosed</li>
                      <li>Aggregate statistics may be included in publications</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Legal Requirements</h3>
                    <p>We may disclose information if required by:</p>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Valid legal process or court order</li>
                      <li>Law enforcement investigations</li>
                      <li>Regulatory compliance requirements</li>
                      <li>Protection of platform security</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'retention' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Data Retention</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Research Data Retention</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Research data may be retained indefinitely for academic purposes</li>
                      <li>Data is retained to support longitudinal research studies</li>
                      <li>Historical data is valuable for research trend analysis</li>
                      <li>Data may be archived for future research use</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Personal Data Retention</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Personal information is retained only as long as necessary</li>
                      <li>Account data is deleted upon account termination</li>
                      <li>Financial data is retained as required by law</li>
                      <li>Research consent data is retained per research protocol</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Data Deletion</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Users may request deletion of personal data</li>
                      <li>Research data may not be deleted due to academic requirements</li>
                      <li>Deletion requests are processed within 30 days</li>
                      <li>Some data may be retained for legal or research purposes</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'rights' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">User Rights and Choices</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Access Rights</h3>
                    <p>Users have the right to:</p>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Access their personal data</li>
                      <li>Request correction of inaccurate data</li>
                      <li>Request deletion of personal data (subject to research requirements)</li>
                      <li>Receive a copy of their data in portable format</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Research Participation</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Users may withdraw from research at any time</li>
                      <li>Withdrawal does not affect data already collected</li>
                      <li>Users may request exclusion from future research</li>
                      <li>Research participation is voluntary</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Communication Preferences</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Users may opt out of non-essential communications</li>
                      <li>Research-related communications may continue</li>
                      <li>Platform updates and security notices are essential</li>
                      <li>Users can update communication preferences</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'security' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white mb-4">Security Measures</h2>
                
                <div className="space-y-4 text-gray-300">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Technical Safeguards</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Encryption of all sensitive data</li>
                      <li>Secure authentication and access controls</li>
                      <li>Regular security updates and patches</li>
                      <li>Network security and monitoring</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Administrative Safeguards</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Staff training on data protection</li>
                      <li>Access controls and user authentication</li>
                      <li>Regular security audits and assessments</li>
                      <li>Incident response and breach notification procedures</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Physical Safeguards</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Secure data centers and server facilities</li>
                      <li>Physical access controls and monitoring</li>
                      <li>Secure disposal of hardware and media</li>
                      <li>Environmental controls and backup systems</li>
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
                    <h3 className="text-xl font-semibold text-white mb-2">Privacy Officer</h3>
                    <p>For privacy-related questions or concerns:</p>
                    <ul className="list-none space-y-1 ml-4">
                      <li>Email: privacy@billionsbounty.edu</li>
                      <li>Address: [Privacy Office Address]</li>
                      <li>Phone: [Privacy Office Phone]</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Research Coordinator</h3>
                    <p>For research-related questions:</p>
                    <ul className="list-none space-y-1 ml-4">
                      <li>Email: research@billionsbounty.edu</li>
                      <li>Address: [Research Office Address]</li>
                      <li>Phone: [Research Office Phone]</li>
                    </ul>
                  </div>

                  <div className="bg-green-500/20 border border-green-500/50 rounded-lg p-4">
                    <h3 className="text-xl font-semibold text-green-400 mb-2">Research Ethics Compliance</h3>
                    <p>This research is conducted under the approval of:</p>
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
              By using this platform, you acknowledge that you have read and understood this privacy policy.
            </p>
            <p className="text-blue-400 font-semibold mt-2">
              This platform is for educational and research purposes only. Your privacy and data protection are important to us.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
