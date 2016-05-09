#!/usr/bin/env python

#=======================================================================
# Authors: Ben Woodcroft, Joel Boyd
#
# Unit tests.
#
# Copyright
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License.
# If not, see <http://www.gnu.org/licenses/>.
#=======================================================================


import unittest
import os.path
import sys

from skbio.tree import TreeNode
from io import StringIO

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')]+sys.path
from graftm.rerooter import Rerooter, TreeParaphyleticException
from graftm.reannotator import Reannotator

class Tests(unittest.TestCase):
    
    def test_reroot_trifurcated_tree_at_longest_child(self):
        test_tree_1 =TreeNode.read(StringIO(u'(A:0.1,B:0.2,(C:0.3,D:0.4):0.5);'))
        test_tree_2 =TreeNode.read(StringIO(u'(A:0.5,B:0.2,(C:0.3,D:0.4):0.1);'))
        test_tree_3 =TreeNode.read(StringIO(u'(A:0.2,B:0.5,(C:0.3,D:0.4):0.1);'))
        
        expected_test_tree_1 ="((A:0.1,B:0.2):0.25,(C:0.3,D:0.4):0.25)root:0;"
        expected_test_tree_2 ="((B:0.2,(C:0.3,D:0.4):0.1):0.25,A:0.25)root:0;"
        expected_test_tree_3 ="((A:0.2,(C:0.3,D:0.4):0.1):0.25,B:0.25)root:0;"
        
        rerooted_test_tree_1 = str(Rerooter().reroot(test_tree_1)).strip()
        rerooted_test_tree_2 = str(Rerooter().reroot(test_tree_2)).strip()
        rerooted_test_tree_3 = str(Rerooter().reroot(test_tree_3)).strip()
        
        self.assertEqual(rerooted_test_tree_1, expected_test_tree_1)
        self.assertEqual(rerooted_test_tree_2, expected_test_tree_2)
        self.assertEqual(rerooted_test_tree_3, expected_test_tree_3)

    def assert_tree_equal_no_labels(self, expected_newick, observed_tree):
        expected = TreeNode.read(StringIO(expected_newick))
        for n in expected.non_tips(): n.name = None
        for n in observed_tree.non_tips(): n.name = None
        self.assertEqual(str(expected), str(observed_tree))
        
    def test_hello_world(self):
        self.assert_tree_equal_no_labels(u'((C,(D,E):2.0):0.0,(A,B):4.0);\n',
             Rerooter().reroot_by_tree(\
                TreeNode.read(StringIO(u'((A,B):1,(C,D):2);')),
                TreeNode.read(StringIO(u'((A,B):1,(C,(D,E):2):3);'))))
        
    def test_hello_world_backwards_compatible(self):
        self.assert_tree_equal_no_labels(u'((C,(D,E):2.0):0.0,(A,B):4.0);\n',
             Reannotator()._reroot_tree_by_old_root(\
                TreeNode.read(StringIO(u'((A,B):1,(C,D):2);')),
                TreeNode.read(StringIO(u'((A,B):1,(C,(D,E):2):3);'))))

    def test_simple(self):
        self.assert_tree_equal_no_labels(u'((C:12.0,(D:13.0,E:14.0):2.0):0,(A:10.0,B:11.0):4.0);\n',
             Rerooter().reroot_by_tree(\
                TreeNode.read(StringIO(u'((A,B):1,(C,D):2);')),
                TreeNode.read(StringIO(u'((C:12,(A:10,B:11)a:4)b:0.5,(D:13,E:14)c:1.5);'))))
        
    def test_extra_unannotated_at_root(self):
        self.assert_tree_equal_no_labels(u'((C:12.0,(D:13.0,E:14.0):2.0):4.0,(F:15.0,(A:10.0,B:11.0):1.0):0.0)root;\n',
             Rerooter().reroot_by_tree(\
                TreeNode.read(StringIO(u'((A,B):1,(C,D):2);')),
                TreeNode.read(StringIO(u'((C:12,((A:10,B:11)d:1,F:15)a:4)b:0.5,(D:13,E:14)c:1.5);'))))
        
        self.assert_tree_equal_no_labels(u'((F:15.0,(C:12.0,a:4.0,(D:13.0,E:14.0):2.0)):0.0,(A:10.0,B:11.0):40.0);\n',
             Rerooter().reroot_by_tree(\
                TreeNode.read(StringIO(u'((A,B):1,(C,D):2);')),
                TreeNode.read(StringIO(u'((C:12,((A:10,B:11)d:40,F:15),a:4)b:0.5,(D:13,E:14)c:1.5);'))))
        
    def test_paraphyletic_at_root(self):
        with self.assertRaises(TreeParaphyleticException):
            Rerooter().reroot_by_tree(\
                TreeNode.read(StringIO(u'((A,B):1,(C,D):2);')),
                TreeNode.read(StringIO(u'((A,D):1,(C,B):2);')))
            
    def test_joel_bug(self):
        tree67 = u'''[
Thu Sep 10 15:55:28 2015: Loaded from /srv/projects/graftm/testing_files/testing_graftM/tmp_01_decorate/67_otus.tree
Thu Sep 10 15:56:18 2015: tree_67_otus saved to /srv/projects/graftm/testing_files/testing_graftM/tmp_01_decorate/67_otus.rerooted.tree
]
((((1928988:0.10866,2909029:0.15809):0.03546,((801940:0.10703,(3825327:0.12686,4298210:0.09398):0.07480):0.02560,729293:0.21465):0.01982):0.02058,((426860:0.16275,219508:0.12556):0.02403,((1128285:0.06200,4455990:0.07954):0.07525,(815912:0.12348,(3770699:0.23707,823009:0.09955):0.04225):0.01489):0.01849):0.01531):0.09184,(((2361381:0.22741,(3779572:0.06720,4363260:0.07438):0.01460):0.04187,(((((((734152:0.13251,4091454:0.12251):0.03552,((576962:0.14097,(1145804:0.14124,3106714:0.14895):0.01964):0.01668,(2014493:0.15560,(3192744:0.11018,(202294:0.07263,1138804:0.08032):0.05015):0.01277):0.01187):0.01016):0.01486,4323734:0.15004):0.00053,(759363:0.05430,4459468:0.04835):0.03216):0.01531,4322265:0.12041):0.01024,(4391683:0.11058,(229854:0.07735,(4336814:0.09937,((150571:0.07911,2730777:0.10930):0.04404,((4042859:0.25381,(717487:0.13914,4363563:0.19585):0.02281):0.02587,(((3190878:0.16480,4452949:0.07312):0.05029,(4015030:0.10339,(4438491:0.04779,(2286116:0.08699,(4251079:0.03657,4349225:0.02256):0.01189):0.01091):0.04963):0.01748):0.02917,(3014179:0.16455,(2170497:0.16101,(2107103:0.22406,951205:0.11633):0.02436):0.02574):0.03041):0.01561):0.02862):0.02589):0.01914):0.01811):0.01347):0.01451,((182569:0.14758,4363259:0.07793):0.04894,696036:0.14901):0.01514):0.01624):0.02659,(3761685:0.11278,4423155:0.16503):0.03965):0.09184);
'''
        tree70 = u'((4423550:0.17275,((4091454:0.108,4427993:0.1045)50:0.01575,((123662:0.06599,(3269889:0.12737,(104534:0.06041,734152:0.09136)20:0.00526)80:0.01669)90:0.01398,(300695:0.10755,225636:0.1317)100:0.0405)0:0.01073)40:0.0128)20:0.00782,(4377103:0.09243,((172946:0.08097,1145804:0.08645)100:0.02986,(1941303:0.0953,4332975:0.09505)90:0.00838)100:0.02206)90:0.0272,((((1931714:0.07012,(4322265:0.10071,4343117:0.13235)100:0.01842)100:0.03116,(((759363:0.05402,4459468:0.0433)100:0.02405,(294612:0.14484,2679839:0.1009)90:0.02132)70:0.01331,((((((730039:0.15444,((4015030:0.11176,(4438491:0.04568,(4349225:0.02406,(2286116:0.08501,(4251079:0.02026,4386156:0.01582)80:0.01016)40:0.0097)80:0.0168)100:0.03826)50:0.01397,(4308961:0.10766,4452949:0.05355)90:0.06215)40:0.01455)50:0.01325,(((1718272:0.12738,(150571:0.08502,(699249:0.03117,2730777:0.03253)100:0.06302)70:0.02174)60:0.03847,(((2107103:0.20025,3190878:0.14435)40:0.03601,(1824285:0.10892,3014179:0.14706)30:0.02039)0:0.01309,((3366304:0.09202,951205:0.07509)100:0.05732,2170497:0.16332)90:0.02722)10:0.01937)0:0.01868,(3064426:0.20791,((1837676:0.14477,(4363563:0.14803,4479774:0.10823)90:0.04638)90:0.03766,(4042859:0.2295,717487:0.15674)40:0.01749)20:0.01416)0:0.01063)0:0.03387)100:0.04795,4336814:0.08037)0:0.02958,(346735:0.11193,4391683:0.07639)60:0.00894)0:0.01312,1142178:0.07594)0:0.01881,(229854:0.0646,4460175:0.09289)90:0.02422)20:0.01731)0:0.01339)0:0.00777,(((2984017:0.05634,4340384:0.07722)80:0.03016,(((4371218:0.13005,(1133483:0.08797,3106714:0.09717)90:0.02053)80:0.02174,(3256066:0.08328,4022282:0.11841)90:0.03619)100:0.03392,((202294:0.06795,1138804:0.07777)100:0.05296,(3192744:0.09608,(2014493:0.11684,(180127:0.06532,4417185:0.0713)100:0.03824)100:0.0368)40:0.01663)70:0.00787)50:0.01733)10:0.0083,(222095:0.1391,(288404:0.13004,(4323734:0.07601,4446882:0.06844)60:0.01661)100:0.02863)40:0.01639)0:0.00846)0:0.0135,(((((1133369:0.07769,4336154:0.07979)100:0.11778,(((708774:0.0822,((114724:0.047,82092:0.04936)100:0.11526,(201206:0.10329,4423155:0.14181)60:0.03138)40:0.01886)80:0.03209,(202302:0.11673,3761685:0.09059)100:0.02325)90:0.02946,(((576962:0.11188,202459:0.09918)90:0.033,(213358:0.0989,(3390949:0.09853,3726184:0.09836)90:0.03298)90:0.02315)20:0.01425,202949:0.15903)0:0.01188)20:0.02709)10:0.01609,((4323100:0.0982,4409929:0.10612)60:0.01386,((696036:0.11283,(203529:0.18615,202449:0.08377)10:0.02209)30:0.02916,((2361381:0.18808,203220:0.10905)100:0.04166,(4363260:0.07208,(3779572:0.04977,114015:0.13268)70:0.02151)70:0.01055)100:0.04229)0:0.01717)0:0.01634)0:0.00519,(539547:0.12233,(4409453:0.14784,(4363259:0.05689,((268769:0.0594,266521:0.05311)100:0.04977,(182569:0.10314,4463866:0.07165)70:0.01505)100:0.04024)80:0.01602)100:0.05088)20:0.02162)0:0.0112,((573196:0.11279,((((3825327:0.11767,4298210:0.09472)100:0.07495,(836195:0.11165,801940:0.09002)100:0.02232)90:0.0347,((1928988:0.1129,(1129716:0.13293,2909029:0.13959)50:0.01858)70:0.02572,(((815912:0.12176,((219508:0.13512,(426860:0.12643,(202758:0.04748,4344033:0.03692)100:0.11429)90:0.0487)20:0.00791,((823117:0.10669,823009:0.0888)90:0.0381,3770699:0.24911)50:0.02136)40:0.02309)30:0.01326,(4455990:0.05381,(1128285:0.06585,4271527:0.03794)70:0.02727)100:0.06911)10:0.01546,4097115:0.09311)30:0.02142)20:0.01039)20:0.02855,(729293:0.18117,3871866:0.11553)90:0.03599)100:0.15854)20:0.02836,150700:0.13922)20:0.02787)0:0.00717)0:0.00859)100;'
        
        old_tree = TreeNode.read(StringIO(tree67))
        tree_to_reroot = TreeNode.read(StringIO(tree70)) 
        new_tree = Rerooter().reroot_by_tree(\
            old_tree,
            tree_to_reroot)
        
        expected_lefts = old_tree.children[0].tips()
        expected_rights = old_tree.children[1].tips()
        for tip in expected_lefts:
            self.assertTrue(tip.name in [t.name for t in new_tree.children[1].tips()])
        for tip in expected_rights:
            self.assertTrue(tip.name in [t.name for t in new_tree.children[0].tips()])
        self.assertEqual(len(list(tree_to_reroot.tips())), len(list(new_tree.tips())))

    @unittest.skip("known failure")
    def test_ben_bug(self):
        new_tree_newick = u'(646366661:0.00571,(646777089:0.01427,(2556226606:0.0,2517129521:0.0):0.04312)0.377:0.01170,((650856936:0.01153,(((((646367708:0.01465,(638201361:0.00187,646622935:0.00573)0.940:0.01352)0.988:0.02634,(2519841469:0.06952,(650856136:0.01840,2506713669:0.02486)0.774:0.00888)0.893:0.01193)0.981:0.03778,((649738338:0.07504,(638155665:0.00613,648151945:0.00304)0.995:0.05973)0.884:0.02836,((650752390:0.11644,(2516847065:0.01707,2520801411:0.03442)0.993:0.04619)0.940:0.03278,(640592705:0.14347,637846211:0.11851)0.971:0.04593)0.940:0.03067)0.943:0.03401)0.998:0.06483,(638168675:0.17080,((649738388:0.09935,((((2540854716:0.00325,2553937573:0.00406)1.000:0.09930,(646533023:0.09868,640592823:0.06908)0.951:0.03770)1.000:0.07636,(650872422:0.05527,(650750471:0.05106,(2516847513:0.01440,2520803234:0.02517)0.998:0.05067)0.947:0.03589)0.074:0.01784)0.786:0.03804,(638155700:0.00445,648151981:0.00284)0.894:0.02131)0.995:0.08448)0.999:0.10690,((KYC55281.1:0.28954,(2540666849:0.26647,(2555938320:0.04589,2518907621:0.04631)0.970:0.05624)1.000:0.12340)0.993:0.09723,(((2515321874:0.26529,((637699780:0.01317,(2540563143:0.01361,(638165755:0.01099,638179449:0.01674)0.558:0.00611)0.964:0.01965)1.000:0.10518,(2502870849:0.06989,(648055573:0.14431,(646706666:0.11338,(637960147:0.03570,(2509663319:0.04930,(2519472088:0.03452,2515107634:0.07709)0.639:0.02134)0.957:0.03004)0.316:0.01755)0.809:0.02055)0.323:0.01213)0.991:0.07286)0.974:0.06071)0.997:0.09000,(650797088:0.06590,(639699575:0.03533,2512008957:0.12951)0.779:0.03900)1.000:0.21062)0.685:0.04985,((((640867801:0.08102,(2507462304:0.07476,(643570914:0.08474,((637897753:0.11959,((2509037835:0.14386,(648194984:0.08665,(648195418:0.04239,2506476786:0.04237)0.993:0.03477)0.668:0.01876)0.510:0.00983,((((640115295:0.06428,2540643958:0.01655)1.000:0.05043,2540643737:0.02645)0.502:0.01269,640115052:0.02482)0.987:0.04272,(2507147269:0.04181,2507146024:0.06962)0.615:0.01449)0.611:0.01456)0.992:0.03807)0.542:0.02193,((2525334810:0.02116,640099739:0.01544)0.785:0.00549,(640100248:0.00446,2525335778:0.02444)0.750:0.00227)1.000:0.12583)0.944:0.03489)0.962:0.04171)0.986:0.04499)0.793:0.02738,2509039570:0.05560)1.000:0.18840,(2505968448:0.05750,(2505971857:0.03133,2512783668:0.02305)0.185:0.01848)0.998:0.08344)0.875:0.04885,2518787893:0.16350)0.868:0.04436)1.000:0.14016)0.957:0.05998)0.998:0.08120)0.984:0.05479)0.999:0.07664,(2506713165:0.01408,((650917784:0.03595,640788680:0.07226)0.510:0.02178,(2519842728:0.03972,(646859549:0.04217,(2511672461:0.01672,(640786544:0.03901,(640793336:0.00334,(640165512:0.02037,641283602:0.00189)0.147:0.00210)0.175:0.00497)0.641:0.01093)0.991:0.02914)1.000:0.05940)0.323:0.02509)0.977:0.02843)0.960:0.02127)0.499:0.01743)0.998:0.03986,(638202197:0.00190,(644970377:0.01516,646623830:0.00752)0.678:0.00364)0.903:0.00939)0.626:0.01605);'
        old_tree_newick = u'(((((646366661:0.00564,((2517129521:0,2556226606:0):0.04302,646777089:0.01412)0.499:0.01173)0.999:0.07494,(638202197:0.0019,(644970377:0.01507,646623830:0.0075)0.738:0.00362)0.872:0.00931)0.635:0.01598,650856936:0.01308)0.995:0.04,(2506713165:0.01171,((640788680:0.07255,650917784:0.03571)0.466:0.02189,(2519842728:0.03945,(646859549:0.04217,(2511672461:0.01668,(640786544:0.03894,(640793336:0.00335,(640165512:0.02038,641283602:0.0019)0.155:0.00211)0.174:0.00496)0.668:0.01095)0.987:0.02908)1.000:0.05973)0.285:0.02499)0.985:0.02844)0.967:0.02183)0.668:0.01914,(((646367708:0.01473,(638201361:0.00188,646622935:0.00578)0.947:0.01381)0.981:0.02381,(2519841469:0.06809,(650856136:0.0182,2506713669:0.02508)0.727:0.0089)0.915:0.01182)0.971:0.03729,((649738338:0.07412,(648151945:0.00339,638155665:0.00581)0.999:0.05834)0.847:0.02714,((650752390:0.11368,(2516847065:0.01707,2520801411:0.03449)0.997:0.04731)0.943:0.033,(640592705:0.14071,637846211:0.11886)0.974:0.04714)0.907:0.02899)0.938:0.03341)0.999:0.06584,(638168675:0.16751,((649738388:0.09339,((((2540854716:0.00327,2553937573:0.00411)1.000:0.1001,(640592823:0.06966,646533023:0.10017)0.945:0.03786)0.999:0.07732,(650872422:0.0565,(650750471:0.05131,(2516847513:0.01447,2520803234:0.02528)0.998:0.05086)0.932:0.03598)0.014:0.01864)0.823:0.03947,(648151981:0.00285,638155700:0.0045)0.891:0.01979)0.998:0.08667)0.999:0.11839,((2540666849:0.25749,(2518907621:0.04615,2555938320:0.04332)0.979:0.0624)1.000:0.20869,(((2515321874:0.27886,((637699780:0.01253,(2540563143:0.01408,(638165755:0.01119,638179449:0.01933)0.559:0.0062)0.973:0.01906)1.000:0.10181,(((2509663319:0.05476,(2515107634:0.07727,2519472088:0.03736)0.549:0.02018)0.970:0.02691,(637960147:0.03454,646706666:0.12022)0.328:0.01393)0.935:0.02456,(2502870849:0.07124,648055573:0.13944)0.419:0.01578)0.997:0.07265)0.976:0.05902)0.992:0.09155,(650797088:0.06773,(639699575:0.03844,2512008957:0.12921)0.700:0.03684)1.000:0.19382)0.774:0.0559,((2518787893:0.1617,(2512783668:0.01562,(2505971857:0.02991,2505968448:0.06931)0.820:0.01544)1.000:0.10132)0.000:0.03917,((640867801:0.07687,(2507462304:0.07769,(((637897753:0.11989,((2509037835:0.14075,(648194984:0.08661,(648195418:0.04254,2506476786:0.04232)0.986:0.0348)0.722:0.0191)0.553:0.00998,((((640115295:0.06424,2540643958:0.01643)1.000:0.05042,2540643737:0.02653)0.542:0.01245,640115052:0.0251)0.986:0.04265,(2507146024:0.06963,2507147269:0.0417)0.641:0.01435)0.611:0.01449)0.989:0.03824)0.424:0.02187,((640099739:0.01547,2525334810:0.02122)0.833:0.00545,(640100248:0.00445,2525335778:0.02442)0.761:0.0023)1.000:0.12528)0.944:0.03961,643570914:0.0938)0.959:0.03885)0.984:0.04627)0.758:0.02972,2509039570:0.05614)1.000:0.19872)0.185:0.04422)0.999:0.13795)0.646:0.06267)0.977:0.07517)0.979:0.05715);'
        old_tree = TreeNode.read(StringIO(old_tree_newick))
        tree_to_reroot = TreeNode.read(StringIO(new_tree_newick))
        new_tree = Rerooter().reroot_by_tree(\
            old_tree,
            tree_to_reroot)
        
        expected_lefts = old_tree.children[0].tips()
        expected_rights = old_tree.children[1].tips()
        for tip in expected_lefts:
            self.assertTrue(tip.name in [t.name for t in new_tree.children[1].tips()])
        for tip in expected_rights:
            self.assertTrue(tip.name in [t.name for t in new_tree.children[0].tips()])
        self.assertEqual(len(list(tree_to_reroot.tips())), len(list(new_tree.tips())))

if __name__ == "__main__":
    unittest.main()
