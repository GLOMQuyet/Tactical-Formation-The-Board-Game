import game.Game;
import main.collections.FastArrayList;
import other.GameLoader;
import other.context.Context;
import other.move.Move;
import other.trial.Trial;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;

/**
 * Random games in Ludii, one JSON line per decision: mover, board owners, every
 * legal move, the pick. Ludii normally stops a game after 1250 turns and scores
 * it as a draw; the folk game has no move limit, so the limit is lifted here.
 * Checked by tools/check_ludii.py.
 */
public class LudiiTrace {
    public static void main(String[] a) throws Exception {
        File lud = new File(a[0]);
        int players = Integer.parseInt(a[1]);
        Random rng = new Random(Long.parseLong(a[2]));
        int games = Integer.parseInt(a[3]);
        int maxDecisions = Integer.parseInt(a[4]);
        Game game = GameLoader.loadGameFromFile(lud, Arrays.asList("Players/" + players));
        game.setMaxTurns(1_000_000);
        game.setMaxMoveLimit(1_000_000);
        int sites = game.board().topology().vertices().size();
        try (PrintWriter out = new PrintWriter(new FileWriter(a[5]))) {
            for (int g = 0; g < games; g++) {
                Trial trial = new Trial(game);
                Context ctx = new Context(game, trial);
                game.start(ctx);
                int decisions = 0;
                while (!trial.over() && decisions < maxDecisions) {
                    FastArrayList<Move> found = game.moves(ctx).moves();
                    List<Move> legal = new ArrayList<>();
                    for (int i = 0; i < found.size(); i++) legal.add(found.get(i));
                    StringBuilder sb = new StringBuilder();
                    sb.append("{\"game\":").append(g).append(",\"mover\":").append(ctx.state().mover());
                    sb.append(",\"board\":").append(owners(ctx, sites)).append(",\"legal\":[");
                    for (int i = 0; i < legal.size(); i++) {
                        Move m = legal.get(i);
                        if (i > 0) sb.append(',');
                        sb.append('[').append(m.from()).append(',').append(m.to()).append(']');
                    }
                    Move pick = legal.get(rng.nextInt(legal.size()));
                    sb.append("],\"pick\":[").append(pick.from()).append(',').append(pick.to()).append("]}");
                    out.println(sb);
                    game.apply(ctx, pick);
                    decisions++;
                }
                StringBuilder sb = new StringBuilder();
                sb.append("{\"game\":").append(g).append(",\"end\":true,\"over\":").append(trial.over());
                sb.append(",\"winners\":").append(Arrays.toString(ctx.winners().toArray()));
                sb.append(",\"ranking\":").append(Arrays.toString(trial.ranking()));
                sb.append(",\"board\":").append(owners(ctx, sites)).append('}');
                out.println(sb);
            }
        }
        System.out.println("games " + games + " written to " + a[5]);
    }

    static String owners(Context ctx, int sites) {
        StringBuilder sb = new StringBuilder("[");
        for (int s = 0; s < sites; s++) {
            if (s > 0) sb.append(',');
            sb.append(ctx.containerState(0).whoVertex(s));
        }
        return sb.append(']').toString();
    }
}
