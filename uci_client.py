import datetime
import os
import re
import select
import subprocess
import time


class UCIClient(object):

	def __init__(self, process_command):
		self._process_command = process_command
		self._engine = self._start_engine()
		self._engine.stdin.write("isready\n")

	def set_position_from_moves_list(self, uci_moves_list):
		self._engine.stdin.write(
			"position startpos moves %s\n" % ' '.join(uci_moves_list)
		)
		return self

	def evaluate_position(self, duration=datetime.timedelta(seconds=3)):
		self._engine.stdin.write(
			"go movetime %d\n" % int(duration.total_seconds()*1000)
		)
		time.sleep((duration + datetime.timedelta(milliseconds=100)).total_seconds())

		evaluation_lines = []
		while reduce(lambda x, y: x+y, select.select([self._engine.stdout], [], [], .3)):
			data = self._engine.stdout.readline().rstrip()
			if data is not None:
				evaluation_lines.append(data)

		print evaluation_lines
		return self._parse_evaluation_lines(evaluation_lines)

	def _start_engine(self):
		return subprocess.Popen(
			[self._process_command],
			stdout=subprocess.PIPE,
			stdin=subprocess.PIPE
		)

	evaluation_line_matcher = re.compile("score cp ([0-9]*)")
	best_move_line_matcher = re.compile("bestmove ([a-z0-9]*)")

	def _parse_evaluation_lines(self, evaluation_lines):
		centipawn_score = 0
		best_move = ''
		match = self.best_move_line_matcher.match(evaluation_lines.pop())
		if match:
			best_move = match.group(1)
		while evaluation_lines:
			match = self.evaluation_line_matcher.search(evaluation_lines.pop())
			if match:
				centipawn_score = int(match.group(1))
				break
		return best_move, centipawn_score


StockfishClient = lambda *args, **kwargs: UCIClient('Stockfish/stockfish', *args, **kwargs)


if __name__ == '__main__':
	uci_client = StockfishClient()
	import ipdb; ipdb.set_trace()