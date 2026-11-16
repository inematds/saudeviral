import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import roteiro_ia as r
class Teste(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)
 def test_nao_escreve_fora_da_edicao(self):
  with self.assertRaises(ValueError):r.salvar(json.dumps({'arquivos':{'../fora':'erro'}}),self.p)
  self.assertEqual(list(self.p.iterdir()),[])
 def test_falta_arquivo_nao_salva_parcial(self):
  with self.assertRaises(ValueError):r.salvar(json.dumps({'arquivos':{'base.md':'fonte','roteiro.json':{'falas':[]}}}),self.p)
  self.assertEqual(list(self.p.iterdir()),[])
 def test_sem_pauta_exclusivo(self):
  with self.assertRaises(ValueError):r.salvar(json.dumps({'arquivos':{'SEM_PAUTA.txt':'sem','base.md':'x'}}),self.p)
  r.salvar(json.dumps({'arquivos':{'SEM_PAUTA.txt':'fontes insuficientes'}}),self.p)
  self.assertIn('insuficientes',(self.p/'SEM_PAUTA.txt').read_text())
 def test_json_invalido_preserva_arquivos(self):
  (self.p/'base.md').write_text('original')
  with self.assertRaises(ValueError):r.salvar(json.dumps({'arquivos':{'base.md':'novo','roteiro.json':'{','legenda.txt':'x'}}),self.p)
  self.assertEqual((self.p/'base.md').read_text(),'original')
 def test_roteiro_valido_salva_objeto_e_limpa_sem_pauta(self):
  (self.p/'SEM_PAUTA.txt').write_text('velho')
  r.salvar(json.dumps({'arquivos':{'base.md':'fonte','roteiro.json':{'falas':[{'id':'f1'}]},'legenda.txt':'legenda'}}),self.p)
  self.assertFalse((self.p/'SEM_PAUTA.txt').exists());self.assertEqual(json.loads((self.p/'roteiro.json').read_text())['falas'][0]['id'],'f1')
 def test_fonte_ausente_para_antes_modelo(self):
  (self.p/'transcritos.txt').write_text('abcDEF123')
  with self.assertRaisesRegex(ValueError,'Transcrição ausente'):r.entradas('',self.p,self.p/'tx')
 def test_citacao_com_escape_preserva_numero_e_texto(self):
  base='| Prazo | Canal | video | data | "teto anual passará\\npara R$ 110.000." |'
  r.salvar(json.dumps({'arquivos':{'base.md':base,'roteiro.json':{'falas':[]},'legenda.txt':'texto'}}),self.p)
  self.assertIn('"teto anual passará para R$ 110.000."',(self.p/'base.md').read_text())
  self.assertNotIn('\\n',(self.p/'base.md').read_text())
 def test_nao_altera_escapes_do_roteiro(self):
  fala='exemplo\\n literal'
  r.salvar(json.dumps({'arquivos':{'base.md':'fonte','roteiro.json':{'falas':[{'fala':fala}]},'legenda.txt':'texto'}}),self.p)
  self.assertEqual(json.loads((self.p/'roteiro.json').read_text())['falas'][0]['fala'],fala)
if __name__=='__main__':unittest.main()
